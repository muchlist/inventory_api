from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
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

    if request.method == 'POST':
        schema = HistoryInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        category_available = ["PC", "CCTV", "DAILY"]
        if data["category"].upper() not in category_available:
            return {"msg": "Field category salah!"}, 400

        if data["category"].upper() != "DAILY":
            if not ObjectId.is_valid(parent_id):
                return {"msg": "Object ID tidak valid"}, 400

        if data["date"] is None:
            data["date"] = datetime.now()
        data["branch"] = claims["branch"]
        data["author"] = claims["name"]

        parent_name = "UNKNOWN"
        if data["category"] == "PC":
            parent = computer_update.update_last_status_computer(parent_id,
                                                                 claims["branch"],
                                                                 f'{data["status"]} : {data["note"]}')
            if parent is None:
                return {"msg": "History parent tidak ditemukan atau berbeda cabang"}, 400
            parent_name = parent["client_name"]

        if data["category"] == "CCTV":
            parent = cctv_update.update_last_status_cctv(parent_id,
                                                         claims["branch"],
                                                         f'{data["status"]} : {data["note"]}')
            if parent is None:
                return {"msg": "History parent tidak ditemukan atau berbeda cabang"}, 400
            parent_name = parent["cctv_name"]

        if data["category"] == "DAILY":
            parent_name = claims["name"] + " DAILY"
            parent_id = get_jwt_identity()

        history_dto = HistoryDto(parent_id,
                                 parent_name,
                                 data["category"],
                                 data["author"],
                                 data["branch"],
                                 data["status"],
                                 data["note"],
                                 data["date"],
                                 get_jwt_identity())

        try:
            history_id = history_update.insert_history(history_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        data["_id"] = history_id
        data["parent_id"] = parent_id
        data["author_id"] = get_jwt_identity()
        data["parent_name"] = parent_name
        data["timestamp"] = datetime.now()

        return jsonify(data), 201

    if request.method == 'GET':
        if not ObjectId.is_valid(parent_id):
            return {"msg": "Object ID tidak valid"}, 400

        try:
            histories = history_query.find_history_for_parent(parent_id)
        except:
            return {"msg": "Gagal memanggil data dari database"}, 500

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
    category = request.args.get("category")
    limit = request.args.get("limit")

    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return {"msg": "limit harus berupa angka"}, 400

    """
        Jika cabang luar kalimantan di includekan ke aplikasi maka filter by branch harus dijadikan
        list dan di querry or ke mongodb
    """
    branch = ""
    if request.args.get("branch"):
        branch = request.args.get("branch")

    # histories = history_query.find_histories_by_branch_by_category(branch, category, limit)
    try:
        histories = history_query.find_histories_by_branch_by_category(branch, category, limit)
    except:
        return {"msg": "Gagal memanggil data dari database"}, 500

    return {"histories": histories}, 200


"""
------------------------------------------------------------------------------
mengambil history per user
api.com/user-history/<Muchis>?limit=20
------------------------------------------------------------------------------
"""


@bp.route("/user-history/<author>", methods=['GET'])
@jwt_required
def get_history_from_author(author):
    limit = request.args.get("limit")

    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return {"msg": "limit harus berupa angka"}, 400

    try:
        histories = history_query.find_history_for_user(author, limit)
    except:
        return {"msg": "Gagal memanggil data dari database"}, 500

    return {"histories": histories}, 200


"""
------------------------------------------------------------------------------
Mendelete history
------------------------------------------------------------------------------
"""


@bp.route("/delete-history/<history_id>", methods=['DELETE'])
@jwt_required
def delete_history(history_id):
    claims = get_jwt_claims()
    if not ObjectId.is_valid(history_id):
        return {"msg": "Object ID tidak valid"}, 400

    # dua jam kurang dari sekarang
    time_limit = datetime.now() - timedelta(hours=2)

    try:
        history = history_update.delete_history(history_id, claims["branch"], time_limit)
    except:
        return {"msg": "Gagal memanggil data dari database"}, 500
    if history is None:
        return {"msg": "Gagal menghapus riwayat, batas waktu dua jam telah tercapai !"}, 400

    return {"msg": "history berhasil dihapus"}, 204
