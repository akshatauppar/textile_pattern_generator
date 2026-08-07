from PIL import Image
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageUpscaler:
    """Tile-based image upscaling for seamless patterns"""
    
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
    
    def upscale(self, image_path, scale_factor=2):
        """
        Upscale image by tiling the original pattern.
        
        Args:
            image_path: Path to original image
            scale_factor: 2 for 2×, 4 for 4×
        
        Returns:
            Path to upscaled image
        """
        try:
            # Open original image
            img = Image.open(image_path)
            original_width, original_height = img.size
            
            logger.info(f"Upscaling {image_path} by {scale_factor}×")
            
            # Calculate new size
            new_width = original_width * scale_factor
            new_height = original_height * scale_factor
            
            # Create new image and tile the pattern
            upscaled = Image.new('RGB', (new_width, new_height))
            
            for y in range(scale_factor):
                for x in range(scale_factor):
                    x_offset = x * original_width
                    y_offset = y * original_height
                    upscaled.paste(img, (x_offset, y_offset))
            
            # Save upscaled image
            base_name = Path(image_path).stem
            ext = Path(image_path).suffix
            upscaled_filename = f"{base_name}_{scale_factor}x{ext}"
            upscaled_path = os.path.join(self.upload_folder, upscaled_filename)
            
            upscaled.save(upscaled_path, quality=95, optimize=True)
            
            logger.info(f"Upscaled image saved: {upscaled_path}")
            return upscaled_filename, (new_width, new_height)
        
        except Exception as e:
            logger.error(f"Upscaling failed: {str(e)}")
            raise
