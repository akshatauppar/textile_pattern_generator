# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify, send_file, current_app
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Generation, User
from app.utils.generator import TextileGenerator
from app.websocket import socketio
import os
from datetime import datetime
from threading import Thread
import logging

logger = logging.getLogger(__name__)

generation_bp = Blueprint('generation', __name__, url_prefix='/api')

# Global generator instance
generator = None


def get_generator():
    """Get or initialize the global generator instance"""
    global generator
    if generator is None:
        generator = TextileGenerator()
    return generator


@generation_bp.route('/styles', methods=['GET'])
def get_styles():
    """Get available textile styles and patterns
    
    Returns:
        200: { styles: [...] }
    """
    return jsonify({
        'styles': current_app.config['SUPPORTED_STYLES']
    }), 200


@generation_bp.route('/generate', methods=['POST'])
def generate():
    """Generate a textile pattern
    
    Headers:
        - Authorization: Bearer <token> (optional)
    
    Body:
        - prompt (str, required): Text description of pattern
        - style (str, required): One of bandhani, batik, ikat
        - pattern (str, optional): Pattern subgroup
        - color_1 (str, optional): Primary color
        - color_2 (str, optional): Secondary color
        - seed (int, optional): Random seed for reproducibility
    
    Returns:
        200: { generation: { id, status, image_url, prompt } }
        400: { error: message }
        401: { error: message }
        500: { error: message }
    """
    data = request.get_json()
    
    # Validate input
    if not data or 'prompt' not in data or 'style' not in data:
        return jsonify({'error': 'Missing prompt and/or style'}), 400
    
    prompt = data.get('prompt', '').strip()
    style = data.get('style', '').strip().lower()
    pattern = data.get('pattern', '').strip().lower() or None
    color_1 = data.get('color_1', '').strip() or None
    color_2 = data.get('color_2', '').strip() or None
    seed = data.get('seed')
    
    # Validate prompt
    if not prompt or len(prompt) < 3:
        return jsonify({'error': 'Prompt must be at least 3 characters'}), 400
    
    # Validate style and pattern
    valid_styles = current_app.config['SUPPORTED_STYLES']
    style_ids = [s['id'] for s in valid_styles]
    
    if style not in style_ids:
        return jsonify({'error': f'Invalid style. Must be one of: {", ".join(style_ids)}'}), 400
    
    # Validate pattern if provided
    if pattern:
        style_config = next((s for s in valid_styles if s['id'] == style), None)
        valid_patterns = [p['id'] for p in style_config.get('patterns', [])]
        if pattern not in valid_patterns:
            return jsonify({'error': f'Invalid pattern for {style}. Must be one of: {", ".join(valid_patterns)}'}), 400
    
    # Validate seed if provided
    if seed is not None:
        try:
            seed = int(seed)
        except (ValueError, TypeError):
            return jsonify({'error': 'Seed must be an integer'}), 400
    
    try:
        # Get user_id if authenticated
        user_id = None
        try:
            user_id = get_jwt_identity()
        except:
            pass  # Allow guest users
        
        # Create generation record
        generation = Generation(
            user_id=user_id,
            prompt=prompt,
            style=style,
            color_1=color_1,
            color_2=color_2,
            seed=seed,
            status='processing'
        )
        
        db.session.add(generation)
        db.session.commit()
        
        # Generate in background thread
        print(f"[DEBUG] Starting thread for generation {generation.id}")
        thread = Thread(
            target=_process_generation,
            args=(current_app._get_current_object(), generation.id, prompt, style, pattern, color_1, color_2, seed)
        )
        thread.daemon = True
        thread.start()
        print(f"[DEBUG] Thread started for generation {generation.id}")
        
        return jsonify({
            'generation': generation.to_dict(include_path=False)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


def _process_generation(app, generation_id, prompt, style, pattern, color_1, color_2, seed):
    """Background task to process generation"""
    print(f"[THREAD] Thread started for generation {generation_id}")
    with app.app_context():
        logger.info(f"Starting background generation for ID {generation_id}")
        print(f"[THREAD] Inside app context for generation {generation_id}")
        try:
            logger.info(f"Getting generator instance...")
            generator_instance = get_generator()
            
            logger.info(f"Starting image generation...")
            # Generate image
            image, actual_seed = generator_instance.generate(
                prompt=prompt,
                style=style,
                pattern=pattern,
                color_1=color_1,
                color_2=color_2,
                seed=seed
            )
            
            logger.info(f"Image generated with seed {actual_seed}, saving...")
            # Save image
            filename = f"textile_{generation_id}_{int(datetime.utcnow().timestamp())}.png"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure upload folder exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            image.save(filepath, format='PNG')
            
            logger.info(f"Image saved to {filepath}, updating database...")
            # Update generation record
            generation = Generation.query.get(generation_id)
            if generation:
                generation.image_path = filename
                generation.status = 'completed'
                generation.completed_at = datetime.utcnow()
                if seed is None:
                    generation.seed = actual_seed
                db.session.commit()
                logger.info(f"Generation {generation_id} completed successfully!")
                
                # Emit WebSocket event
                logger.info(f"[WEBSOCKET] Emitting generation_update for {generation_id} to room generation_{generation_id}")
                socketio.emit('generation_update', {
                    'generation_id': generation_id,
                    'status': 'completed',
                    'data': {
                        'image_url': f'/api/images/{filename}',
                        'prompt': prompt,
                        'seed': actual_seed
                    }
                }, room=f'generation_{generation_id}')
                logger.info(f"[WEBSOCKET] Event emitted successfully for generation {generation_id}")
        
        except Exception as e:
            # Update generation with error
            logger.error(f"Generation {generation_id} failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            generation = Generation.query.get(generation_id)
            if generation:
                generation.status = 'failed'
                generation.error_message = str(e)
                generation.completed_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Generation {generation_id} marked as failed in database")
                
                # Emit WebSocket error event
                logger.info(f"[WEBSOCKET] Emitting failure event for generation {generation_id}")
                socketio.emit('generation_update', {
                    'generation_id': generation_id,
                    'status': 'failed',
                    'data': {
                        'error': str(e)
                    }
                }, room=f'generation_{generation_id}')
                logger.info(f"[WEBSOCKET] Failure event emitted for generation {generation_id}")


@generation_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get generation history for authenticated user
    
    Query Parameters:
        - limit (int): Maximum number of results (default 10, max 100)
        - offset (int): Number of results to skip (default 0)
    
    Returns:
        200: { generations: [...] }
        401: { error: message }
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get pagination parameters
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        offset = int(request.args.get('offset', 0))
    except ValueError:
        return jsonify({'error': 'Invalid pagination parameters'}), 400
    
    if limit < 1 or offset < 0:
        return jsonify({'error': 'Invalid pagination parameters'}), 400
    
    # Get generations
    generations = Generation.query.filter_by(user_id=user_id) \
        .order_by(Generation.created_at.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()
    
    return jsonify({
        'generations': [g.to_dict(include_path=True) for g in generations]
    }), 200


@generation_bp.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    """Serve generated image
    
    Parameters:
        - filename (str): Image filename
    
    Returns:
        200: PNG image file
        404: { error: message }
    """
    # Security: prevent path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Image not found'}), 404
    
    try:
        return send_file(
            filepath,
            mimetype='image/png',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': f'Failed to serve image: {str(e)}'}), 500


@generation_bp.route('/status/<int:generation_id>', methods=['GET'])
def get_generation_status(generation_id):
    """Get status of a generation
    
    Parameters:
        - generation_id (int): Generation ID
    
    Returns:
        200: { generation: {...} }
        404: { error: message }
    """
    generation = Generation.query.get(generation_id)
    
    if not generation:
        return jsonify({'error': 'Generation not found'}), 404
    
    return jsonify({
        'generation': generation.to_dict(include_path=True)
    }), 200


@generation_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint
    
    Returns:
        200: { status, model_loaded, database }
    """
    try:
        # Check database
        db.session.execute(db.text('SELECT 1'))
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    # Check if generator can be loaded
    try:
        generator_instance = get_generator()
        model_loaded = generator_instance.is_loaded()
    except Exception as e:
        model_loaded = False
    
    return jsonify({
        'status': 'healthy' if db_status == 'ok' else 'degraded',
        'model_loaded': model_loaded,
        'database': db_status
    }), 200




@generation_bp.route('/test-generate', methods=['POST'])
def test_generate():
    """Synchronous generation for testing (no background thread)"""
    try:
        print("[TEST] Starting synchronous test generation...")
        data = request.get_json() or {}
        prompt = data.get('prompt', 'test pattern')
        style = data.get('style', 'bandhani')
        
        print(f"[TEST] Getting generator instance...")
        generator_instance = get_generator()
        
        print(f"[TEST] Starting image generation...")
        image, seed = generator_instance.generate(
            prompt=prompt,
            style=style,
            num_inference_steps=10  # Faster for testing
        )
        
        print(f"[TEST] Generation successful! Seed: {seed}")
        return jsonify({
            'success': True,
            'seed': seed,
            'message': 'Generation completed successfully'
        }), 200
        
    except Exception as e:
        print(f"[TEST ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

