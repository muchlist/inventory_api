from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (history_query,
                 history_update,
                 computer_update,
                 cctv_update)
from dto.history_dto import HistoryDto
from input_schemas.history import (HistoryInsertSchema)

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

    if not ObjectId.is_valid(parent_id):
        return {"message": "Object ID tidak valid"}, 400

    if request.method == 'POST':
        schema = HistoryInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        category_available = ["PC", "CCTV"]
        if data["category"].upper() not in category_available:
            return {"message": "Field category salah!"}, 400

        if data["date"] is None:
            data["date"] = datetime.now()
        data["branch"] = claims["branch"]
        data["author"] = claims["name"]

        parent = None
        parent_name = "UNKNOWN"
        if data["category"] == "PC":
            parent = computer_update.update_last_status_computer(parent_id, claims["branch"], data["status"])
            if parent is None:
                return {"message": "History parent tidak ditemukan atau berbeda cabang"}, 400
            parent_name = parent["client_name"]

        if data["category"] == "CCTV":
            parent = cctv_update.update_last_status_cctv(parent_id, claims["branch"], data["status"])
            if parent is None:
                return {"message": "History parent tidak ditemukan atau berbeda cabang"}, 400
            parent_name = parent["cctv_name"]

        history_dto = HistoryDto(parent_id,
                                 parent_name,
                                 data["category"],
                                 data["author"],
                                 data["branch"],
                                 data["status"],
                                 data["note"],
                                 data["date"])

        try:
            history_id = history_update.insert_history(history_dto)
        except:
            return {"message": "Gagal menyimpan data ke database"}, 500

        data["_id"] = history_id
        data["parent_id"] = parent_id
        data["parent_name"] = parent_name
        data["timestamp"] = datetime.now()

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


@bp.route("/histories", methods=['GET'])
@jwt_required
def get_history():
    claims = get_jwt_claims()

    category = request.args.get("category")
    branch = claims["branch"]
    if request.args.get("branch"):
        branch = request.args.get("branch")

    try:
        histories = history_query.find_histories_by_branch_by_category(branch, category)
    except:
        return {"message": "Gagal memanggil data dari database"}, 500

    return {"histories": histories}, 200


"""
------------------------------------------------------------------------------
mengambil history per cabang dan per kategory
api.com/histories?category=PC&branch=BAGENDANG
------------------------------------------------------------------------------
"""


@bp.route("/delete-history/<history_id>", methods=['DELETE'])
@jwt_required
def delete_history(history_id):
    claims = get_jwt_claims()
    if not ObjectId.is_valid(history_id):
        return {"message": "Object ID tidak valid"}, 400

    # dua jam kurang dari sekarang
    time_limit = datetime.now() - timedelta(hours=2)

    try:
        history = history_update.delete_history(history_id, claims["branch"], time_limit)
    except:
        return {"message": "Gagal memanggil data dari database"}, 500
    if history is None:
        return {"message": "Gagal menghapus history, history yang lebih dari dua jam tidak dapat di hapus"}, 400

    return {"message": "history berhasil dihapus"}, 204
