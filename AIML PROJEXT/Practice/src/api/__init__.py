from .handle_request import query_bp
from .auth import auth_bp
from .file_upload import upload_bp


all_auth_blueprints=auth_bp
all_query_blueprints=query_bp
all_upload_blueprints=upload_bp