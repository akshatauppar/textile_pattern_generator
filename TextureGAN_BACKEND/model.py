# model.py
import torch
from torch import nn

# --- Paste your exact Generator class from training here ---
class PeriodicConv2d(nn.Conv2d):
    def forward(self, x): return super().forward(x)

class Generator(nn.Module):
    def __init__(self, text_embed_dim=512, image_embed_dim=512, color_dim=6, latent_dim=256, base_channels=512, image_size=512):
        super().__init__()
        self.text_embed_dim = text_embed_dim
        self.image_embed_dim = image_embed_dim
        self.color_dim = color_dim
        self.latent_dim = latent_dim
        self.base_channels = base_channels
        self.image_size = image_size
        self.max_conditioning_dim = text_embed_dim + image_embed_dim + color_dim + latent_dim
        self.initial_projection = nn.Sequential(
            nn.Linear(self.max_conditioning_dim, 4 * 4 * base_channels),
            nn.LeakyReLU(0.2)
        )
        self.upsample_blocks = nn.ModuleList([
            self._make_upsample_block(base_channels, base_channels),
            self._make_upsample_block(base_channels, base_channels),
            self._make_upsample_block(base_channels, base_channels),
            self._make_upsample_block(base_channels, base_channels // 2),
            self._make_upsample_block(base_channels // 2, base_channels // 4),
            self._make_upsample_block(base_channels // 4, base_channels // 8),
            self._make_upsample_block(base_channels // 8, base_channels // 16),
        ])
        self.output_conv = nn.Sequential(
            PeriodicConv2d(base_channels // 16, 3, kernel_size=3, padding=1),
            nn.Tanh()
        )
    def _make_upsample_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Upsample(scale_factor=2, mode='nearest'),
            PeriodicConv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.InstanceNorm2d(out_channels),
            nn.LeakyReLU(0.2),
            PeriodicConv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.InstanceNorm2d(out_channels),
            nn.LeakyReLU(0.2)
        )
    def forward(self, text_embeddings, colors, noise, image_embeddings=None):
        batch_size = text_embeddings.size(0)
        device = text_embeddings.device
        if image_embeddings is None:
            image_embeddings = torch.zeros(batch_size, self.image_embed_dim, device=device, dtype=text_embeddings.dtype)
        conditioning = torch.cat([text_embeddings, image_embeddings, colors, noise], dim=1)
        x = self.initial_projection(conditioning)
        x = x.view(batch_size, self.base_channels, 4, 4)
        for block in self.upsample_blocks:
            x = block(x)
        x = self.output_conv(x)
        return x

# --- Optional: define a config here for image size, latent dim, etc. ---
class ModelConfig:
    TEXT_EMBED_DIM = 512
    IMAGE_EMBED_DIM = 512
    COLOR_DIM = 6
    LATENT_DIM = 256
    GEN_BASE_CHANNELS = 512
    IMAGE_SIZE = 512