from . import db,bcrypt
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
from datetime import datetime,timezone


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password_hash=db.Column(db.String(128),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    #created_at=db.Column(db.Datetime.utc.now())

    def set_password(self,password):
        self.password_hash=bcrypt.generate_password_hash(password).decode('utf-8')


    def check_password(self,password):
        return bcrypt.check_password_hash(self.password_hash,password)
    

# Create a RefreshToken model
class RefreshToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_revoked = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='refresh_tokens')