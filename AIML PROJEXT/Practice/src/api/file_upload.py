from flask import request,jsonify,Blueprint
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required,get_jwt_identity
import os
from ..services import allowed_file,ALLOWED_EXTENSIONS
from flask import current_app
import logging

upload_bp=Blueprint('file_upload',__name__)

@upload_bp.route('/upload',methods=['POST'])
@jwt_required()
def file_upload():
    if 'file' not in request.files:
        return jsonify({
            "message":"No file part present in Request"
        }),400
    
    file=request.files['file']
    if file.filename=='':
        return jsonify({
            "message":"No selected Filename! "
        }),400
    if not allowed_file(file.filename):
        return jsonify({
            "message":"this file type is not allowed",
            "allowed_extenstions":list(ALLOWED_EXTENSIONS)    
        }),400
    
    file.seek(0,os.SEEK_END)
    size=file.tell()
    file.seek(0)
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    if size>MAX_UPLOAD_SIZE:
        return jsonify(
            {
                'message':'File size is too large allowed only 16mb max file size'
            }
        )
    
    file_name=secure_filename(file.filename)
    UPLOAD_FOLDER=current_app.config['UPLOAD_FOLDER']
    os.makedirs(UPLOAD_FOLDER,exist_ok=True)
    try:
        file_path=os.path.join(UPLOAD_FOLDER,file_name)
        file.save(file_path)
        logging.info(f'file uploaded :{file_name},size:{size}bytes to path: {file_path} by User:{get_jwt_identity()}')
        return jsonify(
            {
                'message':'file uploaded Successfully',
                'filename':file_name,
                'size':size,
                'path':file_path
            }
        ),200
    except Exception as e:
        logging.error(f"File upload failed for user {get_jwt_identity()}: {str(e)}")
        return jsonify({
        'error': 'Failed to save the file. Please try again.'
        }), 500
    



