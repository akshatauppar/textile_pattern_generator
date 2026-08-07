# app/config.py
import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Other default settings

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = os.getenv('DB_URL')
    PORT=os.getenv('PORT')
    JWT_SECRET=os.getenv('SECRET')

class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URL = 'postgresql://user:password@localhost/prod'

# A dictionary to easily get the config class based on an environment variable
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
