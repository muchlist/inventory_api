from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    get_jwt_claims,
)
from input_schemas.history import (HistoryInsertSchema)
from dao import (history_query,
                 history_update)
from dto.history_dto import HistoryDto

from datetime import datetime

bp = Blueprint('history_bp', __name__, url_prefix='/api')


"""
------------------------------------------------------------------------------
Membuat dan mengambil Histories per parent
------------------------------------------------------------------------------
"""
@bp.route("/histories/<parent_id>", methods=['GET', 'POST'])
@jwt_required
def insert_history(parent_id):

    claims = get_jwt_claims()

    if request.method == 'POST':
        schema = HistoryInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if data["date"] is None:
            data["date"] = datetime.now()
        data["branch"] = claims["branch"]
        data["author"] = claims["name"]
        data["parent_id"] = parent_id

        history_dto = HistoryDto(data["parent_id"],
                                 data["parent_name"],
                                 data["category"],
                                 data["author"],
                                 data["branch"],
                                 data["status"],
                                 data["note"],
                                 data["date"])

        try:
            history_update.insert_history(history_dto)
        except:
            return {"message": "Gagal menyimpan data ke database"}, 500
        return jsonify(data), 201

    if request.method == 'GET':
        try:
            histories = history_query.find_history_for_parent(parent_id)
        except:
            return {"message": "Gagal memanggil data dari database"}, 500

        return {"histories": histories}, 200


"""
------------------------------------------------------------------------------
mengambil history per cabang dan per kategory
api.com/histories?category=PC&branch=BAGENDANG
------------------------------------------------------------------------------
"""
@bp.route("/histories/", methods=['GET'])
@jwt_required
def get_history():

    claims = get_jwt_claims()
    category = request.args.get("category")
    branch = request.args.get("branch")

    try:
        histories = history_query.find_histories_by_branch_by_category(branch , category)
    except:
        return {"message": "Gagal memanggil data dari database"}, 500

    return {"histories": histories}, 200
