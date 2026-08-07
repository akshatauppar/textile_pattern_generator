import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from diffusers import (
    StableDiffusionXLPipeline,
    AutoencoderKL,
    UNet2DConditionModel,
    EulerDiscreteScheduler
)
from transformers import CLIPTextModel, CLIPTextModelWithProjection, CLIPTokenizer
from PIL import Image
import logging
from pathlib import Path
from typing import Optional, Tuple
import os

logger = logging.getLogger(__name__)


class CircularConv2d(nn.Module):
    """Wrapper for Conv2d with circular padding for seamless tiling"""
    
    def __init__(self, conv_layer):
        super().__init__()
        self.conv = conv_layer
        
        # Extract padding from original conv layer
        if isinstance(conv_layer.padding, int):
            self.pad_h = self.pad_w = conv_layer.padding
        else:
            self.pad_h, self.pad_w = conv_layer.padding
        
        # Set conv padding to 0 since we'll handle it manually
        self.conv.padding = (0, 0)
    
    def forward(self, x):
        # Apply circular padding
        if self.pad_h > 0 or self.pad_w > 0:
            x = F.pad(x, (self.pad_w, self.pad_w, self.pad_h, self.pad_h), mode='circular')
        
        # Apply convolution
        return self.conv(x)


class TextileGenerator:
    """SDXL-based textile pattern generator with LoRA and circular padding"""
    
    def __init__(self, 
                 model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
                 lora_path: Optional[str] = None):
        """
        Initialize the textile pattern generator
        
        Args:
            model_id: HuggingFace model ID for SDXL base
            lora_path: Path to directory containing LoRA adapter weights
        """
        self.model_id = model_id
        self.lora_path = lora_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype_gpu = torch.float16 if self.device == "cuda" else torch.float32
        self.dtype_cpu = torch.float32
        
        self.pipe = None
        self.vae = None
        self.unet = None
        self.text_encoder = None
        self.text_encoder_2 = None
        self.tokenizer = None
        self.tokenizer_2 = None
        self.scheduler = None
        self._is_loaded = False
        
        logger.info(f"TextileGenerator initialized - Device: {self.device}, GPU dtype: {self.dtype_gpu}")
    
    def _apply_circular_padding_to_vae(self):
        """Apply circular padding to VAE Conv2D layers for seamless tiling"""
        logger.info("Applying circular padding to VAE for seamless patterns...")
        
        def apply_circular_to_module(module, prefix=''):
            """Recursively apply circular padding to Conv2d layers"""
            conv_count = 0
            
            for name, child in list(module.named_children()):
                if isinstance(child, nn.Conv2d):
                    # Replace Conv2d with CircularConv2d
                    setattr(module, name, CircularConv2d(child))
                    conv_count += 1
                else:
                    # Recursively process child modules
                    conv_count += apply_circular_to_module(child, prefix + name + '.')
            
            return conv_count
        
        total_conv = apply_circular_to_module(self.vae)
        logger.info(f"Applied circular padding to {total_conv} Conv2D layers in VAE")
    
    def load_model(self):
        """Load SDXL base model and LoRA adapter with memory optimization"""
        if self._is_loaded:
            logger.info("Model already loaded")
            return
        
        try:
            logger.info(f"Loading SDXL base model from {self.model_id}...")
            
            # Load individual components for better control
            # 1. Load VAE
            logger.info("Loading VAE...")
            self.vae = AutoencoderKL.from_pretrained(
                self.model_id,
                subfolder="vae",
                torch_dtype=self.dtype_gpu
            ).to(self.device)
            
            # Apply circular padding to VAE
            self._apply_circular_padding_to_vae()
            
            # 2. Load UNet with LoRA
            logger.info("Loading UNet...")
            self.unet = UNet2DConditionModel.from_pretrained(
                self.model_id,
                subfolder="unet",
                torch_dtype=self.dtype_gpu
            ).to(self.device)
            
            # Load LoRA weights if provided
            if self.lora_path and os.path.exists(self.lora_path):
                logger.info(f"Loading LoRA adapter from {self.lora_path}...")
                # Load LoRA weights using diffusers
                from peft import PeftModel
                self.unet = PeftModel.from_pretrained(
                    self.unet,
                    self.lora_path,
                    adapter_name="textile_lora"
                )
                logger.info("LoRA adapter loaded successfully")
            
            # 3. Load text encoders (keep on CPU to save VRAM)
            logger.info("Loading text encoders (CPU)...")
            self.text_encoder = CLIPTextModel.from_pretrained(
                self.model_id,
                subfolder="text_encoder",
                torch_dtype=self.dtype_cpu
            ).to("cpu")
            
            self.text_encoder_2 = CLIPTextModelWithProjection.from_pretrained(
                self.model_id,
                subfolder="text_encoder_2",
                torch_dtype=self.dtype_cpu
            ).to("cpu")
            
            # 4. Load tokenizers
            logger.info("Loading tokenizers...")
            self.tokenizer = CLIPTokenizer.from_pretrained(
                self.model_id,
                subfolder="tokenizer"
            )
            
            self.tokenizer_2 = CLIPTokenizer.from_pretrained(
                self.model_id,
                subfolder="tokenizer_2"
            )
            
            # 5. Load scheduler from config (no manual initialization)
            logger.info("Loading scheduler from pretrained config...")
            self.scheduler = EulerDiscreteScheduler.from_pretrained(
                self.model_id,
                subfolder="scheduler"
            )
            logger.info("Scheduler loaded successfully")
            
            # Enable memory optimizations
            if self.device == "cuda":
                try:
                    self.unet.enable_xformers_memory_efficient_attention()
                    self.vae.enable_xformers_memory_efficient_attention()
                    logger.info("xformers memory efficient attention enabled")
                except Exception as e:
                    logger.warning(f"xformers not available: {e}")
                
                # Enable gradient checkpointing for memory savings
                self.unet.enable_gradient_checkpointing()
            
            self._is_loaded = True
            logger.info("Model loaded successfully with circular padding for seamless patterns")
        
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._is_loaded
    
    def generate(
        self,
        prompt: str,
        style: str = "block_print",
        pattern: Optional[str] = None,
        color_1: Optional[str] = None,
        color_2: Optional[str] = None,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        image_size: int = 1024,
    ) -> Tuple[Image.Image, int]:
        """
        Generate a seamless textile pattern
        
        Args:
            prompt: Text description of the pattern
            style: Textile style (bandhani, batik, ikat)
            pattern: Pattern subgroup (e.g., leheriya, geometric_batik, etc.)
            color_1: Primary color (optional)
            color_2: Secondary color (optional)
            num_inference_steps: Number of denoising steps
            guidance_scale: Classifier-free guidance scale
            seed: Random seed for reproducibility
            image_size: Output image size (default 1024x1024)
        
        Returns:
            Tuple of (PIL Image, seed used)
        """
        if not self._is_loaded:
            self.load_model()

        # Clamp num_inference_steps to 10-30 (scheduler limit, min 10 for quality)
        num_inference_steps = max(10, min(num_inference_steps, 30))

        # Set seed
        if seed is None:
            seed = int(torch.randint(0, 2**31, (1,)).item())

        generator = torch.Generator(device=self.device).manual_seed(seed)

        # Build enhanced prompt
        full_prompt = self._build_prompt(prompt, style, pattern, color_1, color_2)
        negative_prompt = self._get_negative_prompt()

        logger.info(f"Generating seamless pattern: {full_prompt[:100]}... (seed: {seed}, steps: {num_inference_steps})")

        try:
            # Encode text prompts on CPU
            with torch.no_grad():
                # Tokenize prompts
                text_inputs = self.tokenizer(
                    full_prompt,
                    padding="max_length",
                    max_length=self.tokenizer.model_max_length,
                    truncation=True,
                    return_tensors="pt"
                )
                
                text_inputs_2 = self.tokenizer_2(
                    full_prompt,
                    padding="max_length",
                    max_length=self.tokenizer_2.model_max_length,
                    truncation=True,
                    return_tensors="pt"
                )
                
                # Encode with text encoders (on CPU)
                prompt_embeds = self.text_encoder(
                    text_inputs.input_ids.to("cpu"),
                    output_hidden_states=True
                )
                pooled_prompt_embeds = prompt_embeds[0]
                prompt_embeds = prompt_embeds.hidden_states[-2]
                
                prompt_embeds_2 = self.text_encoder_2(
                    text_inputs_2.input_ids.to("cpu"),
                    output_hidden_states=True
                )
                pooled_prompt_embeds_2 = prompt_embeds_2[0]
                prompt_embeds_2 = prompt_embeds_2.hidden_states[-2]
                
                # Concatenate embeddings
                prompt_embeds = torch.cat([prompt_embeds, prompt_embeds_2], dim=-1)
                
                # Move to GPU for inference
                prompt_embeds = prompt_embeds.to(self.device, dtype=self.dtype_gpu)
                pooled_prompt_embeds = pooled_prompt_embeds_2.to(self.device, dtype=self.dtype_gpu)
                
                # Encode negative prompt
                neg_inputs = self.tokenizer(
                    negative_prompt,
                    padding="max_length",
                    max_length=self.tokenizer.model_max_length,
                    truncation=True,
                    return_tensors="pt"
                )
                
                neg_inputs_2 = self.tokenizer_2(
                    negative_prompt,
                    padding="max_length",
                    max_length=self.tokenizer_2.model_max_length,
                    truncation=True,
                    return_tensors="pt"
                )
                
                neg_embeds = self.text_encoder(
                    neg_inputs.input_ids.to("cpu"),
                    output_hidden_states=True
                )
                neg_pooled = neg_embeds[0]
                neg_embeds = neg_embeds.hidden_states[-2]
                
                neg_embeds_2 = self.text_encoder_2(
                    neg_inputs_2.input_ids.to("cpu"),
                    output_hidden_states=True
                )
                neg_pooled_2 = neg_embeds_2[0]
                neg_embeds_2 = neg_embeds_2.hidden_states[-2]
                
                neg_embeds = torch.cat([neg_embeds, neg_embeds_2], dim=-1)
                neg_embeds = neg_embeds.to(self.device, dtype=self.dtype_gpu)
                neg_pooled = neg_pooled_2.to(self.device, dtype=self.dtype_gpu)
                
                # Prepare latents
                latent_shape = (1, 4, image_size // 8, image_size // 8)
                latents = torch.randn(
                    latent_shape,
                    generator=generator,
                    device=self.device,
                    dtype=self.dtype_gpu
                )
                
                # Scale latents
                latents = latents * self.scheduler.init_noise_sigma
                
                # Set timesteps
                self.scheduler.set_timesteps(num_inference_steps, device=self.device)
                
                # Denoising loop
                for i, t in enumerate(self.scheduler.timesteps):
                    # Expand latents for classifier-free guidance
                    latent_model_input = torch.cat([latents] * 2)
                    latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
                    
                    # Prepare added_cond_kwargs
                    added_cond_kwargs = {
                        "text_embeds": torch.cat([neg_pooled, pooled_prompt_embeds]),
                        "time_ids": torch.cat([
                            torch.tensor([[image_size, image_size, 0, 0, image_size, image_size]], device=self.device, dtype=self.dtype_gpu),
                            torch.tensor([[image_size, image_size, 0, 0, image_size, image_size]], device=self.device, dtype=self.dtype_gpu)
                        ])
                    }
                    
                    # Predict noise
                    encoder_hidden_states = torch.cat([neg_embeds, prompt_embeds])
                    noise_pred = self.unet(
                        latent_model_input,
                        t,
                        encoder_hidden_states=encoder_hidden_states,
                        added_cond_kwargs=added_cond_kwargs,
                        return_dict=False
                    )[0]
                    
                    # Perform classifier-free guidance
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                    
                    # Compute previous noisy sample
                    latents = self.scheduler.step(noise_pred, t, latents, return_dict=False)[0]
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"Denoising step {i + 1}/{num_inference_steps}")
                
                # Decode latents to image (VAE with circular padding)
                latents = latents / self.vae.config.scaling_factor
                image = self.vae.decode(latents, return_dict=False)[0]
                
                # Convert to PIL
                image = (image / 2 + 0.5).clamp(0, 1)
                image = image.cpu().permute(0, 2, 3, 1).float().numpy()
                image = (image[0] * 255).round().astype("uint8")
                image = Image.fromarray(image)
                
                # Clear cache
                if self.device == "cuda":
                    torch.cuda.empty_cache()
                
                logger.info(f"Pattern generated successfully (seamless with circular padding)")
                return image, seed
        
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            if self.device == "cuda":
                torch.cuda.empty_cache()
            raise
    
    def _build_prompt(
        self,
        base_prompt: str,
        style: str,
        pattern: Optional[str],
        color_1: Optional[str],
        color_2: Optional[str],
    ) -> str:
        """Build enhanced prompt with style, pattern and color information"""
        style_descriptions = {
            "bandhani": "traditional tie-dye bandhani pattern, intricate circular motifs, symmetrical design",
            "batik": "wax-resist batik pattern, traditional technique, artistic design",
            "ikat": "resist-dyed ikat textile, abstract geometric patterns, blurred edges",
        }
        
        pattern_descriptions = {
            # Bandhani patterns
            "leheriya": "diagonal wavy lines, flowing movement",
            "shikari": "hunting pattern, wildlife inspired",
            "mothra": "circular motifs and circles",
            "rajasthani_tie": "traditional Rajasthani tie variations",
            "mandala": "circular mandala design, spiritual geometry",
            # Batik patterns
            "geometric_batik": "geometric wax patterns, angular shapes",
            "floral_batik": "floral wax designs, botanical themes",
            "traditional_batik": "traditional Indonesian batik, classic motifs",
            "wax_resist": "contemporary wax resist technique",
            "crackle": "crackle effect pattern, aged texture",
            # Ikat patterns
            "striped_ikat": "striped ikat pattern, linear design",
            "diamond_ikat": "diamond shaped motifs, geometric layout",
            "blurred_motif": "characteristic blurred edges, resist dye effect",
            "traditional_ikat": "traditional ikat weave, classic structure",
            "woven_pattern": "woven ikat patterns, thread interactions",
        }
        
        style_desc = style_descriptions.get(style, "traditional textile pattern")
        pattern_desc = pattern_descriptions.get(pattern, "") if pattern else ""
        
        prompt = f"{base_prompt}, {style_desc}"
        if pattern_desc:
            prompt += f", {pattern_desc}"
        
        prompt += ", seamless pattern, tileable"
        
        if color_1:
            prompt += f", primary color {color_1}"
        if color_2:
            prompt += f", secondary color {color_2}"
        
        prompt += ", high quality, detailed, professional, textile design"
        
        return prompt
    
    def _get_negative_prompt(self) -> str:
        """Get negative prompt for better generation"""
        return (
            "ugly, distorted, blurry, low quality, watermark, text, "
            "human, face, people, figure, bad proportions, "
            "deformed, asymmetrical, irregular, noise"
        )
    
    def unload_model(self):
        """Unload model to free memory"""
        if self._is_loaded:
            self.pipe = None
            self.scheduler = None
            self._is_loaded = False
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            logger.info("Model unloaded")
