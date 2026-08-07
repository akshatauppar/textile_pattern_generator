import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'textile_generator')
    DB_USER = os.getenv('DB_USER', 'textile_user')
    DB_PASS = os.getenv('DB_PASS', 'textile_pass')
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paths
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MODEL_PATH = os.getenv('MODEL_PATH', '../models')
    
    # Generation defaults
    DEFAULT_STEPS = 30
    DEFAULT_GUIDANCE = 7.5
    IMAGE_SIZE = 1024
    IMAGE_FORMAT = 'PNG'
    
    # SDXL Model settings
    SDXL_MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
    LORA_ADAPTER_PATH = os.path.join(MODEL_PATH, "adapter_config.json")
    
    # Supported styles and patterns
    SUPPORTED_STYLES = [
        {
            "id": "bandhani", 
            "name": "Bandhani", 
            "description": "Traditional tie-dye patterns",
            "patterns": [
                {"id": "leheriya", "name": "Leheriya", "description": "Diagonal wavy lines"},
                {"id": "shikari", "name": "Shikari", "description": "Hunting pattern"},
                {"id": "mothra", "name": "Mothra", "description": "Circular motifs"},
                {"id": "rajasthani_tie", "name": "Rajasthani Tie", "description": "Traditional tie variations"},
                {"id": "mandala", "name": "Mandala", "description": "Circular mandala design"},
            ]
        },
        {
            "id": "batik", 
            "name": "Batik", 
            "description": "Wax-resist dyeing technique",
            "patterns": [
                {"id": "geometric_batik", "name": "Geometric", "description": "Geometric wax patterns"},
                {"id": "floral_batik", "name": "Floral", "description": "Floral wax designs"},
                {"id": "traditional_batik", "name": "Traditional", "description": "Traditional Indonesian batik"},
                {"id": "wax_resist", "name": "Wax Resist", "description": "Contemporary wax resist"},
                {"id": "crackle", "name": "Crackle", "description": "Crackle effect pattern"},
            ]
        },
        {
            "id": "ikat", 
            "name": "Ikat", 
            "description": "Resist-dyed textile patterns",
            "patterns": [
                {"id": "striped_ikat", "name": "Striped", "description": "Striped ikat pattern"},
                {"id": "diamond_ikat", "name": "Diamond", "description": "Diamond shaped motifs"},
                {"id": "blurred_motif", "name": "Blurred Motif", "description": "Characteristic blurred edges"},
                {"id": "traditional_ikat", "name": "Traditional", "description": "Traditional ikat weave"},
                {"id": "woven_pattern", "name": "Woven Pattern", "description": "Woven ikat patterns"},
            ]
        },
    ]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Use SQLite for easy development (no PostgreSQL setup needed)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///textile_generator.db'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Strong secrets should be supplied via environment in real deployments
    SECRET_KEY = os.getenv('SECRET_KEY', 'replace-with-strong-secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'replace-with-strong-jwt-secret')
    REQUIRE_STRONG_SECRETS = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
