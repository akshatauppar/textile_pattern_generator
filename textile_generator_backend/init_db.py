#!/usr/bin/env python
"""
Database initialization and migration script
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.models import db, User, Generation
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database"""
    app = create_app()
    
    with app.app_context():
        # Drop all tables (use with caution!)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Verify tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in database: {', '.join(tables)}")
        
        return True


def seed_data():
    """Add sample data to database"""
    app = create_app()
    
    with app.app_context():
        # Check if data already exists
        if User.query.first() is not None:
            logger.info("Database already contains data, skipping seeding")
            return False
        
        try:
            # Create sample user
            user = User(
                username='demo_user',
                email='demo@textile.local'
            )
            user.set_password('demo_password')
            
            db.session.add(user)
            db.session.commit()
            
            logger.info("Sample data added successfully")
            logger.info("Sample user: username='demo_user', password='demo_password'")
            return True
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to seed data: {str(e)}")
            return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database management')
    parser.add_argument('--init', action='store_true', help='Initialize database')
    parser.add_argument('--seed', action='store_true', help='Seed sample data')
    parser.add_argument('--reset', action='store_true', help='Reset and reinitialize database')
    
    args = parser.parse_args()
    
    if args.reset:
        logger.warning("Resetting database...")
        app = create_app()
        with app.app_context():
            db.drop_all()
            logger.info("Database tables dropped")
        init_db()
        seed_data()
    elif args.init:
        init_db()
    elif args.seed:
        seed_data()
    else:
        # Default: initialize and seed
        if init_db():
            seed_data()
