from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    generations = db.relationship('Generation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Generation(db.Model):
    """Model for storing textile generation records"""
    __tablename__ = 'generations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable for guest users
    prompt = db.Column(db.Text, nullable=False)
    style = db.Column(db.String(50), nullable=False)  # bandhani, ikat, block_print, paisley
    color_1 = db.Column(db.String(50), nullable=True)
    color_2 = db.Column(db.String(50), nullable=True)
    seed = db.Column(db.Integer, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)  # filename only
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self, include_path=False):
        """Convert generation to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'prompt': self.prompt,
            'style': self.style,
            'color_1': self.color_1,
            'color_2': self.color_2,
            'seed': self.seed,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
        if include_path and self.image_path:
            data['image_url'] = f'/api/images/{self.image_path}'
        if self.error_message:
            data['error_message'] = self.error_message
        return data
    
    def __repr__(self):
        return f'<Generation {self.id} - {self.status}>'
