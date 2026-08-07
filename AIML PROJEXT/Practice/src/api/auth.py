
from flask import Blueprint,jsonify,request
from .auth_schema import Register_Schema,Login_Schema
from marshmallow import ValidationError
from ..models import User
from .. import db
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity,create_refresh_token
from werkzeug.utils import secure_filename
import os
from datetime import timedelta

auth_bp=Blueprint('auth',__name__)

register_schema=Register_Schema()
login_schema=Login_Schema()
   
@auth_bp.route('/register',methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({
            "error":"Invalid request only json data is allowed!"
        }),415

    data=request.get_json()
    if not data:
        return jsonify({
            "error":"No json data provided"
        }),400
    
    try:
        validated_data=register_schema.load(data)
        print(validated_data)
        username=validated_data['username']
        email=validated_data['email']
        password=validated_data['password']
    #registration logic 
        if User.query.filter_by(username=username).first():
            return jsonify({
                "message":"User already Exists"
            }),409
        
        new_user=User(username=username, email=email)
        new_user.set_password(password=password)
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token=create_refresh_token(identity=str(new_user.id),expires_delta=timedelta(days=30))
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({
                "message":"user registred Successsfully ",
                "user_id":new_user.id,
                "access_token": access_token,
                'refresh_token':refresh_token
            }),201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "message":"an error occured! failed to create user"
            }),500

    except ValidationError as err:
        return jsonify(
            {
                "error":"Validation Error",
                "Required":err.messages
            }
        ),400

@auth_bp.route('/login',methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({
            "message":"Invalid Data format only json data is allowed"
        }),400
    
    data=request.get_json()
    try:
        validated_data=login_schema.load(data=data)
        username=validated_data['username']
        password=validated_data['password']
        try:
            user=User.query.filter_by(username=username).first()
            if not user:
                return jsonify({
                    'message':'Username or password is not correct'
                }),401
          
            if user.check_password(password=password):
                access_token=create_access_token(identity=str(user.id))
                refresh_token=create_refresh_token(identity=str(user.id),expires_delta=timedelta(days=30))
                return jsonify({
                    "message":"Logged In Successfully",
                    "user_id":user.id,
                    "access_token":access_token,
                    "refresh_token":refresh_token
                }),200
            return jsonify({
                'message':'Username or password is not correct'
            }),401
        
        except Exception as e:
            return jsonify({
                'message':'an error occured login failed',
                'error':str(e)
            }),500
                
    except ValidationError as e:
        return jsonify({
            "message":"Validation error Check the email or password",
            "error":e.messages
        }),400

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        "message": f"Hello {user.username}! This is a protected route.",
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    new_access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Token refreshed successfully",
        "access_token": new_access_token
    }), 200
