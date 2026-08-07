from flask import request,jsonify

def safe_json():
    data = request.get_json(silent=True)
    
    if data is None:
        return jsonify({"error": "Invalid or missing JSON"}), 400
        
    return jsonify({"received": data})

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

