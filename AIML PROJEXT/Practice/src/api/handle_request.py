
from flask import Blueprint,jsonify,request


query_bp=Blueprint('queries',__name__)
@query_bp.route("/query-example")
def handle_queies():
    language=request.args.get('language')
    framework=request.args.get('framework')
    website=request.args.get('website')

    return jsonify({
        "language":language,
        "framework":framework,
        "website":website
    })


    
