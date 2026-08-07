"""
WSGI entry point for production deployment
Use with Gunicorn, uWSGI, or other WSGI servers
"""

from app import create_app
import os

# Create app with production config
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    # This is for development only
    # For production, use: gunicorn -w 4 wsgi:app
    app.run()
