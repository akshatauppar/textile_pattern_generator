# app_state.py
import torch
from transformers import CLIPModel, CLIPTokenizer
from model import Generator, ModelConfig
import os

# Device for inference (prefer GPU if available).
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load Generator weights and instantiate model
def load_generator():
    weights_path = os.path.join("models", "generator_final.pt")
    generator = Generator(
        text_embed_dim=ModelConfig.TEXT_EMBED_DIM,
        image_embed_dim=ModelConfig.IMAGE_EMBED_DIM,
        color_dim=ModelConfig.COLOR_DIM,
        latent_dim=ModelConfig.LATENT_DIM,
        base_channels=ModelConfig.GEN_BASE_CHANNELS,
        image_size=ModelConfig.IMAGE_SIZE
    ).to(device)
    generator.load_state_dict(torch.load(weights_path, map_location=device))
    generator.eval()
    return generator

# Load CLIP model and tokenizer
def load_clip():
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_model.eval()
    clip_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
    return clip_model, clip_tokenizer

# Global (will be loaded at startup)
generator = None
clip_model = None
clip_tokenizer = None