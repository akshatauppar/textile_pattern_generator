from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Generation
from app.utils.upscaler import ImageUpscaler
import logging
import os

logger = logging.getLogger(__name__)

upscale_bp = Blueprint('upscale', __name__, url_prefix='/api')
upscaler = None

def get_upscaler():
    """Get or initialize upscaler"""
    global upscaler
    if upscaler is None:
        upload_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'uploads'
        )
        upscaler = ImageUpscaler(upload_folder)
    return upscaler

@upscale_bp.route('/upscale', methods=['POST'])
def upscale():
    """
    Upscale a generated seamless pattern.
    
    Body:
        {
            "generation_id": 123,
            "scale": 2  # or 4
        }
    
    Returns:
        {
            "upscaled_url": "/api/images/gen_123_2x.png",
            "resolution": "2048×2048",
            "method": "tiled"
        }
    """
    try:
        data = request.get_json()
        generation_id = data.get('generation_id')
        scale = data.get('scale', 2)
        
        # Validate scale
        if scale not in [2, 4]:
            return jsonify({'error': 'Scale must be 2 or 4'}), 400
        
        # Get generation record
        generation = Generation.query.get(generation_id)
        if not generation:
            return jsonify({'error': 'Generation not found'}), 404
        
        if generation.status != 'completed':
            return jsonify({'error': 'Generation not completed'}), 400
        
        if not generation.image_path:
            return jsonify({'error': 'No image to upscale'}), 400
        
        # Get upscaler
        upscaler_instance = get_upscaler()
        
        # Build full image path
        image_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            generation.image_path
        )
        
        # Perform upscaling
        logger.info(f"Upscaling generation {generation_id} by {scale}×")
        upscaled_filename, new_resolution = upscaler_instance.upscale(
            image_path,
            scale
        )
        
        logger.info(f"Upscaling successful: {upscaled_filename}")
        
        return jsonify({
            'upscaled_url': f'/api/images/{upscaled_filename}',
            'resolution': f'{new_resolution[0]}×{new_resolution[1]}',
            'method': 'tiled',
            'filename': upscaled_filename
        }), 200
    
    except Exception as e:
        logger.error(f"Upscaling error: {str(e)}")
        return jsonify({'error': f'Upscaling failed: {str(e)}'}), 500
