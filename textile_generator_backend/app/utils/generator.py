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
        style: str = "bandhani",
        pattern: Optional[str] = None,
        color_1: Optional[str] = None,
        color_2: Optional[str] = None,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        image_size: int = 1024,
        reference_image: Optional[str] = None,
    ) -> Tuple[Image.Image, int]:
        """
        Generate a seamless textile pattern
        
        Args:
            prompt: Text description of the pattern
            style: Textile style (bandhani, batik, ikat, block_print, paisley)
            pattern: Pattern subgroup
            color_1: Primary color (optional)
            color_2: Secondary color (optional)
            num_inference_steps: Number of denoising steps
            guidance_scale: Classifier-free guidance scale
            seed: Random seed for reproducibility
            image_size: Output image size (default 1024x1024)
            reference_image: Base64 or path to reference image (optional)
        
        Returns:
            Tuple of (PIL Image, seed used)
        """
        if seed is None:
            # Generate random seed using numpy to avoid torch requirement on CPU if needed
            seed = int(np.random.randint(0, 2**31 - 1))

        if self.device == "cpu":
            logger.info("CPU environment detected - utilizing fast procedural generator fallback.")
            img = self._generate_procedural(prompt, style, pattern, color_1, color_2, seed, image_size, reference_image)
            return img, seed

        if not self._is_loaded:
            self.load_model()

        # Create a request-specific scheduler to avoid cross-thread state modification
        scheduler = EulerDiscreteScheduler.from_config(self.scheduler.config)

        # Clamp num_inference_steps to 1-30 (SDXL-Turbo supports 1-4 steps)
        num_inference_steps = max(1, min(num_inference_steps, 30))

        # Set seed
        generator = torch.Generator(device=self.device).manual_seed(seed)

        # Build enhanced prompt
        full_prompt = self._build_prompt(prompt, style, pattern, color_1, color_2, reference_image)
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
                latents = latents * scheduler.init_noise_sigma
                
                # Set timesteps
                scheduler.set_timesteps(num_inference_steps, device=self.device)
                
                # Denoising loop
                for i, t in enumerate(scheduler.timesteps):
                    # Expand latents for classifier-free guidance
                    latent_model_input = torch.cat([latents] * 2)
                    latent_model_input = scheduler.scale_model_input(latent_model_input, t)
                    
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
                    latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
                    
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
        reference_image: Optional[str] = None,
    ) -> str:
        """Build enhanced prompt with style, pattern and color information"""
        style_descriptions = {
            "bandhani": "traditional Indian tie-dye bandhani pattern, intricate circular dot motifs, symmetrical design, Gujarat Rajasthan craft",
            "batik": "wax-resist batik textile art, crackle dye streaks, traditional Indonesian and Indian motifs, artistic resist dyeing",
            "ikat": "resist-dyed ikat woven textile, abstract geometric patterns, blurred feathered edges, warp weft interactions",
            "block_print": "traditional hand-carved wooden block print textile, Jaipuri floral buta motifs, Ajrakh geometric stars, intricate stamped details",
            "paisley": "ornate Kashmiri paisley kalka pattern, curving teardrop floral motifs, Persian buta swirls, royal zardozi embroidery style",
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
            # Block print patterns
            "jaipuri_floral": "delicate Jaipuri botanical block print motifs, leaf stems and buds",
            "ajrakh_star": "intricate Ajrakh geometric stars and symmetrical grid stamps",
            "buta_stamp": "classical repeating floral buta block stamp with ornate borders",
            "geometric_lattice": "interlocking lattice jaal pattern",
            # Paisley patterns
            "royal_paisley": "grand ornate kalka teardrop paisley filled with intricate blossoms",
            "floral_buta": "curling botanical paisley bouquet with fine scrolling vines",
            "zardozi_swirl": "luxurious shimmering floral swirls and golden teardrop flourishes",
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
        
        if reference_image:
            prompt += ", styled and harmonized with uploaded reference image features"
            
        prompt += ", high quality, detailed, professional, textile design"
        
        return prompt
    
    def _get_negative_prompt(self) -> str:
        """Get negative prompt for better generation"""
        return (
            "ugly, distorted, blurry, low quality, watermark, text, "
            "human, face, people, figure, bad proportions, "
            "deformed, asymmetrical, irregular, noise"
        )

    def _generate_procedural(
        self,
        prompt: str,
        style: str,
        pattern: Optional[str],
        color_1: Optional[str],
        color_2: Optional[str],
        seed_val: int,
        image_size: int,
        reference_image: Optional[str] = None
    ) -> Image.Image:
        """Procedural fallback to generate highly aesthetic seamless patterns on CPU"""
        from PIL import Image, ImageDraw, ImageFilter
        import numpy as np
        import hashlib
        import random
        import base64
        import io

        # Mix prompt hash with seed to ensure unique prompts produce unique patterns
        prompt_hash = int(hashlib.md5(prompt.encode('utf-8')).hexdigest(), 16) % (2**31 - 1)
        mixed_seed = (seed_val + prompt_hash) % (2**31 - 1)
        random.seed(mixed_seed)
        np.random.seed(mixed_seed)

        # Extract colors if reference image provided
        extracted_c1 = None
        extracted_c2 = None
        if reference_image:
            try:
                ref_bytes = None
                if reference_image.startswith('data:image'):
                    # data URI
                    header, encoded = reference_image.split(',', 1)
                    ref_bytes = base64.b64decode(encoded)
                elif os.path.exists(reference_image):
                    with open(reference_image, 'rb') as f:
                        ref_bytes = f.read()
                if ref_bytes:
                    ref_img = Image.open(io.BytesIO(ref_bytes)).convert("RGB").resize((64, 64))
                    ref_arr = np.array(ref_img).reshape(-1, 3)
                    # Get dominant 2 colors using simple clustering/quantization
                    quantized = ref_img.quantize(colors=4).convert("RGB")
                    dom_colors = quantized.getcolors(maxcolors=100)
                    if dom_colors and len(dom_colors) >= 2:
                        dom_sorted = sorted(dom_colors, key=lambda x: x[0], reverse=True)
                        extracted_c1 = dom_sorted[0][1]
                        extracted_c2 = dom_sorted[1][1] if len(dom_sorted) > 1 else dom_sorted[0][1]
            except Exception as ref_err:
                logger.warning(f"Failed to extract color from reference image: {ref_err}")

        # Try to call Pollinations.ai for high-quality prompt-specific AI image generation!
        try:
            import urllib.request
            import urllib.parse
            
            logger.info(f"Calling Pollinations.ai API for prompt: {prompt}")
            
            style_desc = f"{style} style Indian textile" if style else "textile pattern"
            pattern_desc = f"{pattern} pattern" if pattern else ""
            c1_str = color_1 or (f"rgb{extracted_c1}" if extracted_c1 else "")
            c2_str = color_2 or (f"rgb{extracted_c2}" if extracted_c2 else "")
            color_desc = f"with primary color {c1_str} and secondary color {c2_str}" if (c1_str or c2_str) else ""
            
            full_prompt_sd = f"seamless tileable textile pattern design, {style_desc}, {pattern_desc}, {prompt}, {color_desc}, high quality fabric texture, top-down view flat, 8k resolution"
            encoded_prompt = urllib.parse.quote(full_prompt_sd)
            
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={image_size}&height={image_size}&seed={mixed_seed}&nologo=true&private=true"
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                img_data = response.read()
                img_loaded = Image.open(io.BytesIO(img_data))
                logger.info("Successfully fetched pattern from Pollinations.ai!")
                return img_loaded
        except Exception as api_err:
            logger.warning(f"Pollinations.ai fallback ({str(api_err)}) - using high-precision procedural synthesis.")

        # Create canvas
        img = Image.new("RGB", (image_size, image_size), "#ffffff")
        draw = ImageDraw.Draw(img)

        # Color parser helper
        def parse_color(c, default):
            if not c:
                return default
            if isinstance(c, (list, tuple)):
                if len(c) >= 3:
                    return (int(c[0]), int(c[1]), int(c[2]))
                return default
            c_str = str(c).strip().lower()
            if c_str.startswith('#'):
                c_str = c_str[1:]
            if len(c_str) == 6:
                try:
                    return (int(c_str[0:2], 16), int(c_str[2:4], 16), int(c_str[4:6], 16))
                except ValueError:
                    pass
            elif len(c_str) == 3:
                try:
                    return (int(c_str[0]*2, 16), int(c_str[1]*2, 16), int(c_str[2]*2, 16))
                except ValueError:
                    pass
            color_map = {
                'red': (220, 38, 38),
                'maroon': (128, 0, 0),
                'blue': (30, 58, 138),
                'indigo': (49, 46, 129),
                'green': (5, 150, 105),
                'emerald': (16, 185, 129),
                'gold': (245, 158, 11),
                'yellow': (250, 204, 21),
                'black': (17, 24, 39),
                'white': (255, 255, 255),
                'cream': (254, 243, 199),
                'beige': (245, 245, 220),
                'purple': (126, 34, 206),
                'crimson': (159, 18, 57),
            }
            return color_map.get(c_str, default)

        # Base style colors setup
        if style == "bandhani":
            c1 = parse_color(color_1, extracted_c1 or (136, 19, 55))    # Deep Crimson / Maroon
            c2 = parse_color(color_2, extracted_c2 or (245, 158, 11))   # Marigold Gold
        elif style == "batik":
            c1 = parse_color(color_1, extracted_c1 or (30, 58, 138))    # Royal Indigo / Navy
            c2 = parse_color(color_2, extracted_c2 or (254, 243, 199))  # Warm Cream
        elif style == "block_print":
            c1 = parse_color(color_1, extracted_c1 or (15, 23, 42))     # Deep Ajrakh Black / Navy
            c2 = parse_color(color_2, extracted_c2 or (217, 119, 6))    # Ochre Gold / Rust
        elif style == "paisley":
            c1 = parse_color(color_1, extracted_c1 or (76, 29, 149))    # Royal Purple
            c2 = parse_color(color_2, extracted_c2 or (245, 158, 11))   # Zardozi Gold
        else: # ikat or other
            c1 = parse_color(color_1, extracted_c1 or (123, 17, 19))    # Crimson Weave
            c2 = parse_color(color_2, extracted_c2 or (230, 223, 211))  # Off-white

        width_img = image_size
        height_img = image_size

        # Wrap-around coordinate draw helpers to make the pattern 100% seamless
        def draw_wrap_circle(draw_obj, cx, cy, r, fill, outline=None, width=1):
            for dx in [-width_img, 0, width_img]:
                for dy in [-height_img, 0, height_img]:
                    draw_obj.ellipse(
                        [cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                        fill=fill,
                        outline=outline,
                        width=width
                    )

        def draw_wrap_rect(draw_obj, x1, y1, x2, y2, fill, outline=None, width=1):
            w = x2 - x1
            h = y2 - y1
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            for dx in [-width_img, 0, width_img]:
                for dy in [-height_img, 0, height_img]:
                    draw_obj.rectangle(
                        [cx + dx - w/2, cy + dy - h/2, cx + dx + w/2, cy + dy + h/2],
                        fill=fill,
                        outline=outline,
                        width=width
                    )

        def draw_wrap_polygon(draw_obj, points, fill, outline=None, width=1):
            for dx in [-width_img, 0, width_img]:
                for dy in [-height_img, 0, height_img]:
                    offset_points = [(p[0] + dx, p[1] + dy) for p in points]
                    draw_obj.polygon(offset_points, fill=fill, outline=outline, width=width)

        def draw_wrap_line(draw_obj, p1, p2, fill, width=1):
            x1, y1 = p1
            x2, y2 = p2
            for dx in [-width_img, 0, width_img]:
                for dy in [-height_img, 0, height_img]:
                    draw_obj.line(
                        [(x1 + dx, y1 + dy), (x2 + dx, y2 + dy)],
                        fill=fill,
                        width=width
                    )

        # Dot helper for Bandhani tie-dye knot resist
        def draw_bandhani_dot(draw_obj, cx, cy, fill_color, center_color, r_outer=5, r_inner=2):
            draw_wrap_circle(draw_obj, cx, cy, r_outer, fill_color)
            draw_wrap_circle(draw_obj, cx, cy, r_inner, center_color)

        # ----------------------------------------------------
        # Style 1: Bandhani
        # ----------------------------------------------------
        if style == "bandhani":
            # Draw base color background
            draw.rectangle([0, 0, image_size, image_size], fill=c1)
            
            if pattern == "leheriya":
                num_stripes = np.random.randint(4, 8)
                amplitude = np.random.uniform(10, 22)
                frequency = np.random.randint(2, 5)
                direction = np.random.choice([-1, 1])
                for s in range(num_stripes):
                    offset = s * (image_size / num_stripes)
                    for x in range(0, image_size, 8):
                        y = (direction * x + offset) % image_size
                        y_wavy = y + amplitude * np.sin(2 * frequency * np.pi * x / image_size)
                        draw_bandhani_dot(draw, x, y_wavy, c2, c1, 5, 2)
                        draw_bandhani_dot(draw, x, (y_wavy + 16) % image_size, c2, c1, 3.5, 1.5)
            
            elif pattern == "shikari":
                grid_size = np.random.choice([96, 128])
                petal_count = np.random.randint(6, 9)
                r_petal = np.random.randint(14, 22)
                for x in range(0, image_size, grid_size):
                    for y in range(0, image_size, grid_size):
                        cx, cy = x + grid_size/2, y + grid_size/2
                        draw_bandhani_dot(draw, cx, cy, c2, c1, 6, 2.5)
                        for idx in range(petal_count):
                            angle = (idx / petal_count) * 360
                            rad = np.radians(angle)
                            px = cx + r_petal * np.cos(rad)
                            py = cy + r_petal * np.sin(rad)
                            draw_bandhani_dot(draw, px, py, c2, c1, 4.5, 1.8)
                            
                        leaf_offset = grid_size / 3.5
                        for dx, dy in [(-leaf_offset, -leaf_offset), (leaf_offset, -leaf_offset), 
                                       (-leaf_offset, leaf_offset), (leaf_offset, leaf_offset)]:
                            draw_bandhani_dot(draw, cx + dx, cy + dy, c2, c1, 4, 1.5)
            
            elif pattern == "mothra":
                grid_size = np.random.choice([48, 64, 80])
                for x in range(0, image_size, grid_size):
                    for y in range(0, image_size, grid_size):
                        for step in range(8):
                            t = step / 8
                            draw_bandhani_dot(draw, x + t * grid_size, y + t * grid_size, c2, c1, 4, 1.5)
                            draw_bandhani_dot(draw, x + t * grid_size, y + (1 - t) * grid_size, c2, c1, 4, 1.5)
                        draw_bandhani_dot(draw, x + grid_size/2, y + grid_size/2, c2, c1, 6, 2)
            
            elif pattern == "rajasthani_tie":
                block_size = np.random.choice([96, 128])
                for bx in range(0, image_size, block_size):
                    for by in range(0, image_size, block_size):
                        for i in range(0, block_size, 12):
                            draw_bandhani_dot(draw, bx + i, by, c2, c1, 4, 1.5)
                            draw_bandhani_dot(draw, bx + i, by + block_size, c2, c1, 4, 1.5)
                            draw_bandhani_dot(draw, bx, by + i, c2, c1, 4, 1.5)
                            draw_bandhani_dot(draw, bx + block_size, by + i, c2, c1, 4, 1.5)
                        
                        cx, cy = bx + block_size/2, by + block_size/2
                        r = block_size / 3
                        num_dots = int(2 * np.pi * r / 11)
                        for idx in range(num_dots):
                            angle = (idx / num_dots) * 360
                            rad = np.radians(angle)
                            draw_bandhani_dot(draw, cx + r * np.cos(rad), cy + r * np.sin(rad), c2, c1, 4.5, 1.8)
                        draw_bandhani_dot(draw, cx, cy, c2, c1, 6, 2)
            
            else: # mandala or default
                def draw_mandala(cx, cy):
                    num_rings = np.random.randint(3, 6)
                    for r_idx in range(num_rings):
                        r = (r_idx + 1) * 18
                        num_dots = int(2 * np.pi * r / 10)
                        c_fill = c2 if r_idx % 2 == 0 else c1
                        c_bg = c1 if r_idx % 2 == 0 else c2
                        for i in range(num_dots):
                            angle = (i / num_dots) * 360
                            rad = np.radians(angle)
                            draw_bandhani_dot(draw, cx + r * np.cos(rad), cy + r * np.sin(rad), c_fill, c_bg, 4.5, 1.8)
                    draw_bandhani_dot(draw, cx, cy, c2, c1, 7, 2.5)
                
                draw_mandala(0, 0)
                draw_mandala(image_size/2, image_size/2)

        # ----------------------------------------------------
        # Style 2: Batik
        # ----------------------------------------------------
        elif style == "batik":
            draw.rectangle([0, 0, image_size, image_size], fill=c1)
            
            if pattern == "geometric_batik":
                grid = np.random.choice([48, 64, 80])
                for x in range(0, image_size, grid):
                    for y in range(0, image_size, grid):
                        fill = c2 if ((x // grid) + (y // grid)) % 2 == 0 else c1
                        pts = [(x + grid/2, y), (x + grid, y + grid/2), (x + grid/2, y + grid), (x, y + grid/2)]
                        draw_wrap_polygon(draw, pts, fill=fill)
                        fill_inner = c1 if ((x // grid) + (y // grid)) % 2 == 0 else c2
                        pts_in = [(x + grid/2, y + 10), (x + grid - 10, y + grid/2), (x + grid/2, y + grid - 10), (x + 10, y + grid/2)]
                        draw_wrap_polygon(draw, pts_in, fill=fill_inner)
            
            elif pattern == "floral_batik":
                grid = np.random.choice([96, 128])
                for x in range(0, image_size, grid):
                    for y in range(0, image_size, grid):
                        cx, cy = x + grid/2, y + grid/2
                        draw_wrap_line(draw, (x, y), (cx, cy), c2, width=3)
                        draw_wrap_circle(draw, cx - 25, cy - 10, 10, fill=c2)
                        draw_wrap_circle(draw, cx + 25, cy + 10, 10, fill=c2)
                        num_petals = np.random.randint(6, 9)
                        for angle_idx in range(num_petals):
                            angle = (angle_idx / num_petals) * 360
                            rad = np.radians(angle)
                            px = cx + 20 * np.cos(rad)
                            py = cy + 20 * np.sin(rad)
                            draw_wrap_circle(draw, px, py, 12, fill=c2)
                        draw_wrap_circle(draw, cx, cy, 14, fill=c1)
            
            elif pattern == "traditional_batik":
                grid = 64
                for x in range(0, image_size, grid):
                    for y in range(0, image_size, grid):
                        draw_wrap_circle(draw, x + grid/2, y + grid/2, grid/2 + 2, fill=None, outline=c2, width=3)
                        cx, cy = x + grid/2, y + grid/2
                        draw_wrap_circle(draw, cx, cy, 6, fill=c2)
                        draw_wrap_circle(draw, cx - 12, cy, 4, fill=c2)
                        draw_wrap_circle(draw, cx + 12, cy, 4, fill=c2)
                        draw_wrap_circle(draw, cx, cy - 12, 4, fill=c2)
                        draw_wrap_circle(draw, cx, cy + 12, 4, fill=c2)
            
            else: # crackle or wax_resist
                for i in range(25):
                    cx = int((i * 111 + 47) % image_size)
                    cy = int((i * 223 + 19) % image_size)
                    draw_wrap_circle(draw, cx, cy, 32, fill=c2)
            
            # Overlay characteristic Batik wax crackles
            num_cracks = 60 if pattern == "crackle" else 35
            crack_color = c2 if pattern == "crackle" else c2
            for i in range(num_cracks):
                x = int((i * 387 + 109) % image_size)
                y = int((i * 713 + 347) % image_size)
                points = [(x, y)]
                angle = (i * 135) % 360
                rad = np.radians(angle)
                for _ in range(8):
                    step_len = 15 + (i % 15)
                    x += int(step_len * np.cos(rad) + np.random.randint(-4, 5))
                    y += int(step_len * np.sin(rad) + np.random.randint(-4, 5))
                    points.append((x, y))
                for p_idx in range(len(points) - 1):
                    draw_wrap_line(draw, points[p_idx], points[p_idx+1], crack_color, width=1)

        # ----------------------------------------------------
        # Style 3: Block Print (Jaipuri / Ajrakh)
        # ----------------------------------------------------
        elif style == "block_print":
            draw.rectangle([0, 0, image_size, image_size], fill=c1)
            grid = 96
            for x in range(0, image_size, grid):
                for y in range(0, image_size, grid):
                    cx, cy = x + grid/2, y + grid/2
                    # Grid frame border
                    draw_wrap_rect(draw, x + 4, y + 4, x + grid - 4, y + grid - 4, fill=None, outline=c2, width=2)
                    
                    if pattern == "ajrakh_star":
                        # 8-point geometric star stamp
                        for a in range(0, 360, 45):
                            rad = np.radians(a)
                            rad_inner = np.radians(a + 22.5)
                            p1 = (cx + 26 * np.cos(rad), cy + 26 * np.sin(rad))
                            p2 = (cx + 12 * np.cos(rad_inner), cy + 12 * np.sin(rad_inner))
                            p3 = (cx, cy)
                            draw_wrap_polygon(draw, [p1, p2, p3], fill=c2)
                        draw_wrap_circle(draw, cx, cy, 6, fill=c1)
                    else:
                        # Jaipuri floral buta stamp
                        draw_wrap_circle(draw, cx, cy, 10, fill=c2)
                        for p in range(6):
                            ang = np.radians(p * 60)
                            draw_wrap_circle(draw, cx + 18 * np.cos(ang), cy + 18 * np.sin(ang), 8, fill=c2)
                            draw_wrap_circle(draw, cx + 18 * np.cos(ang), cy + 18 * np.sin(ang), 3, fill=c1)
                        # Stem and foliage
                        draw_wrap_line(draw, (cx, cy + 10), (cx, cy + 32), fill=c2, width=3)
                        draw_wrap_line(draw, (cx, cy + 22), (cx - 10, cy + 14), fill=c2, width=2)
                        draw_wrap_line(draw, (cx, cy + 22), (cx + 10, cy + 14), fill=c2, width=2)

        # ----------------------------------------------------
        # Style 4: Paisley (Kalka / Teardrop)
        # ----------------------------------------------------
        elif style == "paisley":
            draw.rectangle([0, 0, image_size, image_size], fill=c1)
            grid = 128
            for x in range(0, image_size, grid):
                for y in range(0, image_size, grid):
                    cx, cy = x + grid/2, y + grid/2
                    # Paisley Kalka teardrop parametric curve
                    pts = []
                    for t in np.linspace(0, 2*np.pi, 36):
                        # Parametric teardrop curve formula
                        r = 28 * (1 - np.sin(t))
                        px = cx + r * np.cos(t) * 0.9
                        py = cy + r * np.sin(t) - 10
                        pts.append((px, py))
                    draw_wrap_polygon(draw, pts, fill=c2)
                    # Inner swirling core
                    draw_wrap_circle(draw, cx, cy - 8, 12, fill=c1)
                    draw_wrap_circle(draw, cx, cy - 8, 5, fill=c2)
                    # Surrounding floral florets
                    for f in range(5):
                        fa = np.radians(f * 45 - 90)
                        draw_wrap_circle(draw, cx + 24 * np.cos(fa), cy + 8 + 24 * np.sin(fa), 4, fill=c2)

        # ----------------------------------------------------
        # Style 5: Ikat
        # ----------------------------------------------------
        else:
            draw.rectangle([0, 0, image_size, image_size], fill=c1)
            
            if pattern == "striped_ikat":
                stripe_w = np.random.randint(24, 48)
                for x in range(0, image_size, stripe_w * 2):
                    draw_wrap_rect(draw, x, 0, x + stripe_w, image_size, fill=c2)
                    draw_wrap_rect(draw, x + stripe_w/2 - 2, 0, x + stripe_w/2 + 2, image_size, fill=c1)
            
            elif pattern == "diamond_ikat":
                grid = np.random.choice([80, 96, 112])
                for x in range(0, image_size, grid):
                    for y in range(0, image_size, grid):
                        for level in range(3):
                            fill_color = c2 if level % 2 == 0 else c1
                            offset = level * (grid / 9)
                            pts = [
                                (x + grid/2, y + offset),
                                (x + grid - offset, y + grid/2),
                                (x + grid/2, y + grid - offset),
                                (x + offset, y + grid/2)
                            ]
                            draw_wrap_polygon(draw, pts, fill=fill_color)
            
            else: # traditional ikat or default
                grid = 128
                star_points = 8
                for x in range(0, image_size, grid):
                    for y in range(0, image_size, grid):
                        cx, cy = x + grid/2, y + grid/2
                        pts = []
                        for i in range(star_points * 2):
                            angle = i * (360 / (star_points * 2))
                            rad = np.radians(angle)
                            r = 35 if i % 2 == 0 else 18
                            pts.append((cx + r * np.cos(rad), cy + r * np.sin(rad)))
                        draw_wrap_polygon(draw, pts, fill=c2)
                        draw_wrap_circle(draw, cx, cy, 10, fill=c1)
                        draw_wrap_circle(draw, cx, cy, 3, fill=c2)

        # Apply warp bleed effect (Ikat thread shift)
        if style == "ikat":
            img_np = np.array(img)
            h, w, c = img_np.shape
            bleed_img = img_np.copy()
            np.random.seed(mixed_seed)
            for col in range(w):
                shift = np.random.randint(-5, 6)
                bleed_img[:, col] = np.roll(img_np[:, col], shift, axis=0)
            img = Image.fromarray(bleed_img)

        # Apply cloth weave texture overlay (warp/weft simulation)
        img_np = np.array(img).astype(np.float32)
        h, w, c = img_np.shape
        np.random.seed(mixed_seed + 999)
        warp = np.sin(np.arange(w) * (2 * np.pi / 2.0)) * 6.0
        weft = np.sin(np.arange(h) * (2 * np.pi / 2.0)) * 6.0
        weave = (warp[None, :, None] + weft[:, None, None]) / 2.0
        noise = np.random.normal(0, 3.0, img_np.shape)
        img_np = np.clip(img_np + weave + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_np)

        return img

    def unload_model(self):
        """Unload model to free memory"""
        if self._is_loaded:
            self.pipe = None

            self.scheduler = None
            self._is_loaded = False
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            logger.info("Model unloaded")
