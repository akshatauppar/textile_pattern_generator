# app/__init__.py

import os
from flask import Flask
from .config import config_by_name
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB
# Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    jwt=JWTManager(app)
    app.config['JWT_SECRET_KEY']=os.getenv('SECRET')
    app.config['JWT_TOKEN_LOCATION'] = ['headers'] 
    app.config['JWT_REFRESH_TOKEN_LOCATION'] = ['headers']
    # In create_app() function
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # 1 hour expiration
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # 30 days for refresh tokens
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    bcrypt.init_app(app)
    migrate=Migrate(app,db=db)

    CORS(app,resources={r"*": {"origins": "*"}})
    app.config.from_object(config_by_name[config_name])
    
    # Import and register blueprints after app is created
    from .api import all_auth_blueprints, all_query_blueprints,all_upload_blueprints
    app.register_blueprint(all_auth_blueprints, url_prefix='/auth')
    app.register_blueprint(all_query_blueprints,url_prefix='/')
    app.register_blueprint(all_upload_blueprints,url_prefix='/')
    
    return app
