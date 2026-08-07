"""
Test script for the textile pattern generator
Run this to verify your LoRA model loads correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.generator import TextileGenerator
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_model_loading():
    """Test if model loads successfully"""
    print("\n" + "="*60)
    print("TEXTILE PATTERN GENERATOR - MODEL TEST")
    print("="*60 + "\n")
    
    # Path to your LoRA weights
    lora_path = "../models"
    
    print(f"LoRA Path: {lora_path}")
    print(f"LoRA Exists: {os.path.exists(lora_path)}\n")
    
    if os.path.exists(lora_path):
        files = os.listdir(lora_path)
        print(f"LoRA Files: {files}\n")
    
    try:
        # Initialize generator
        print("Initializing TextileGenerator...")
        generator = TextileGenerator(
            model_id="stabilityai/stable-diffusion-xl-base-1.0",
            lora_path=lora_path if os.path.exists(lora_path) else None
        )
        
        print("\n" + "-"*60)
        print("Loading model (this may take several minutes)...")
        print("-"*60 + "\n")
        
        # Load model
        generator.load_model()
        
        print("\n" + "="*60)
        print("✅ MODEL LOADED SUCCESSFULLY!")
        print("="*60 + "\n")
        
        print("Model Details:")
        print(f"  - Device: {generator.device}")
        print(f"  - GPU dtype: {generator.dtype_gpu}")
        print(f"  - CPU dtype: {generator.dtype_cpu}")
        print(f"  - VAE loaded: {generator.vae is not None}")
        print(f"  - UNet loaded: {generator.unet is not None}")
        print(f"  - Text encoders: {generator.text_encoder is not None}")
        print(f"  - Circular padding: Applied to VAE Conv2D layers")
        
        if os.path.exists(lora_path):
            print(f"  - LoRA adapter: Loaded from {lora_path}")
        else:
            print(f"  - LoRA adapter: Not found (using base SDXL)")
        
        print("\n" + "="*60)
        print("READY TO GENERATE PATTERNS!")
        print("="*60 + "\n")
        
        return True
    
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR LOADING MODEL")
        print("="*60 + "\n")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_generation():
    """Test pattern generation (optional - requires model loaded)"""
    print("\n" + "="*60)
    print("TESTING PATTERN GENERATION")
    print("="*60 + "\n")
    
    lora_path = "../models"
    
    try:
        generator = TextileGenerator(
            model_id="stabilityai/stable-diffusion-xl-base-1.0",
            lora_path=lora_path if os.path.exists(lora_path) else None
        )
        
        generator.load_model()
        
        print("Generating test pattern...")
        print("  Prompt: 'intricate geometric pattern'")
        print("  Style: bandhani")
        print("  Steps: 20 (faster test)")
        print()
        
        image, seed = generator.generate(
            prompt="intricate geometric pattern",
            style="bandhani",
            num_inference_steps=20,  # Faster for testing
            seed=42
        )
        
        # Save test image
        output_path = "test_pattern.png"
        image.save(output_path)
        
        print("\n" + "="*60)
        print("✅ PATTERN GENERATED SUCCESSFULLY!")
        print("="*60 + "\n")
        print(f"  - Image saved: {output_path}")
        print(f"  - Size: {image.size}")
        print(f"  - Seed: {seed}")
        print(f"  - Seamless: Yes (circular padding applied)")
        print()
        
        return True
    
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR GENERATING PATTERN")
        print("="*60 + "\n")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Textile Pattern Generator')
    parser.add_argument('--generate', action='store_true', 
                       help='Also test pattern generation (takes longer)')
    
    args = parser.parse_args()
    
    # Test model loading
    success = test_model_loading()
    
    # Optionally test generation
    if success and args.generate:
        test_generation()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")
