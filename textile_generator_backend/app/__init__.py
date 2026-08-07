from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
import logging
from config import config
from app.models import db
from app.routes.auth import auth_bp
from app.routes.generation import generation_bp
from app.routes.upscale import upscale_bp
from app.websocket import socketio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Application factory function"""
    
    # Determine config
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    if config_name not in config:
        config_name = 'development'
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Warn if production secrets are not set
    if config_name == 'production':
        secret = app.config.get('SECRET_KEY')
        jwt_secret = app.config.get('JWT_SECRET_KEY')
        placeholders = {'replace-with-strong-secret', 'replace-with-strong-jwt-secret', 'dev-secret-key', 'jwt-secret-key'}
        if not secret or secret in placeholders or not jwt_secret or jwt_secret in placeholders:
            logger.warning("Production secrets are not set securely. Please set SECRET_KEY and JWT_SECRET_KEY environment variables.")
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    JWTManager(app)
    socketio.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(generation_bp)
    app.register_blueprint(upscale_bp)
    
    # Create uploads folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)
        logger.info(f"Created upload folder: {upload_folder}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': 'Textile Pattern Generator API',
            'version': '1.0.0',
            'status': 'running'
        }), 200
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'message': 'Textile Pattern Generator API operational'
        }), 200
    
    # Database context
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
    
    logger.info(f"Flask app created with config: {config_name}")
    
    return app

