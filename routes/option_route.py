from flask import Blueprint, jsonify

from utils.options import options_json_object

bp = Blueprint('options_bp', __name__, url_prefix='/api')

EXPIRED_TOKEN = 15

"""
------------------------------------------------------------------------------
options
------------------------------------------------------------------------------
"""


@bp.route('/ping', methods=['GET'])
def ping():
    return {"message": "pong"}, 200


@bp.route('/options_version', methods=['GET'])
def option_version():
    return {"message": options_json_object["version"]}, 200


@bp.route('/options', methods=['GET'])
def option():
    return jsonify(options_json_object), 200
