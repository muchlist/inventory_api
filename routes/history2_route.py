from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
)
from marshmallow import ValidationError

from dao import (
    history2_query,
    history2_update,
    computer_update,
    computer_query,
    cctv_update,
    cctv_query,
    handheld_update,
    handheld_query,
)
from dto.history2_dto import (
    HistoryDto2, EditHistoryDto2
)
from input_schemas.history2 import HistoryInsertSchema, HistoryEditSchema
from utils.options import options_json_object

bp = Blueprint('history2_bp', __name__, url_prefix='/api')

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

        category_available = ["PC", "CCTV", "DAILY", "HANDHELD"]
        if data["category"].upper() not in category_available:
            return {"msg": "Field category salah!"}, 400

        # karena daily tidak memiliki parent maka perlu dicek ObjekID user nya
        if data["category"].upper() != "DAILY":
            if not ObjectId.is_valid(parent_id):
                return {"msg": "Object ID tidak valid"}, 400

        if data["date"] is None:
            data["date"] = datetime.now()

        if ("end_date" in data) and (data["end_date"] is not None):
            end_date = data["end_date"]
            time_delta = end_date - data["date"]
            total_second = time_delta.total_seconds()
            duration = int(total_second / 60)
        else:
            end_date = None
            duration = 0

        data["branch"] = claims["branch"]
        data["author"] = claims["name"]

        # ketika menambahkan history menggunakan ID pc , cctv, handheld maka harus mengupdate insiden di
        # masing masing insiden unit ID, sambil mengupdate mengambil parent name.

        history_id = ObjectId()

        parent_name = "UNKNOWN"
        if data["complete_status"] < 2:
            # Jika historynya !complete / (complete_status == 0) / (complete_status == 1) masukkan kedalam case
            case = f'{data["status"]} : {data["note"]}'
            if data["complete_status"] == 1:
                case = f'##PENDING## {data["status"]} : {data["note"]}'

            if data["category"] == "PC":
                parent = computer_update.insert_case_computer(
                    parent_id,
                    claims["branch"],
                    str(history_id),
                    case
                )
                if parent is None:
                    return {"msg": "History parent tidak ditemukan atau berbeda cabang"}, 400
                parent_name = parent["client_name"]

            if data["category"] == "CCTV":
                parent = cctv_update.insert_case_cctv(parent_id,
                                                      claims["branch"],
                                                      str(history_id),
                                                      case
                                                      )
                if parent is None:
                    return {"msg": "History parent tidak ditemukan atau berbeda cabang"}, 400
                parent_name = parent["cctv_name"]

            if data["category"] == "HANDHELD":
                parent = handheld_update.insert_case_handheld(parent_id,
                                                              claims["branch"],
                                                              str(history_id),
                                                              case)
                if parent is None:
                    return {"msg": "History parent tidak ditemukan atau berbeda cabang"}, 400
                parent_name = parent["handheld_name"]
        else:

            """jika tidak complete_status = 2 maka tidak perlu menambahkan case
               sehingga menemukan parent_name harus di get"""

            if data["category"] == "PC":
                parent = computer_query.get_computer(parent_id)
                if parent is None:
                    return {"msg": "History parent tidak ditemukan atau berbeda cabang"}, 400
                parent_name = parent["client_name"]

            if data["category"] == "CCTV":
                parent = cctv_query.get_cctv(parent_id)
                if parent is None:
                    return {"msg": "History parent tidak ditemukan atau berbeda cabang"}, 400
                parent_name = parent["cctv_name"]

            if data["category"] == "HANDHELD":
                parent = handheld_query.get_handheld(parent_id)
                if parent is None:
                    return {"msg": "History parent tidak ditemukan atau berbeda cabang"}, 400
                parent_name = parent["handheld_name"]

        if data["category"] == "DAILY":
            parent_name = "GENERAL"
            parent_id = get_jwt_identity()

        history_dto = HistoryDto2(
            author=claims["name"],
            author_id=get_jwt_identity(),
            branch=claims["branch"],
            location=data["location"],
            status=data["status"],
            created_at=datetime.now(),
            timestamp=datetime.now(),
            date=data["date"],
            end_date=end_date,
            note=data["note"],
            parent_id=parent_id,
            parent_name=parent_name,
            duration=duration,
            resolve_note=data["resolve_note"],
            complete_status=data["complete_status"],
            category=data["category"],
            updated_by=claims["name"],
            updated_by_id=get_jwt_identity(),
        )

        try:
            history_id_result = history2_update.insert_history(history_id, history_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return {"msg": f"History berhasil dibuat {history_id_result}"}, 200

    if request.method == 'GET':
        if not ObjectId.is_valid(parent_id):
            return {"msg": "Object ID tidak valid"}, 400

        try:
            histories = history2_query.find_history_for_parent(parent_id)
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
    complete_status = request.args.get("complete_status")

    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return {"msg": "limit harus berupa angka"}, 400

    if complete_status or complete_status == 0:
        try:
            complete_status = int(complete_status)
        except ValueError:
            return {"msg": "complete_status harus berupa angka"}, 400

    """
        Jika cabang luar kalimantan di includekan ke aplikasi maka filter by branch harus dijadikan
        list dan di querry or ke mongodb
    """

    branch = ""
    if request.args.get("branch"):
        branch = request.args.get("branch")

    # histories = history_query.find_histories_by_branch_by_category(branch, category, limit)
    try:
        histories = history2_query.find_histories_by_branch_by_category(branch=branch,
                                                                        category=category,
                                                                        complete_status=complete_status,
                                                                        limit=limit)
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
        histories = history2_query.find_history_for_user(author, limit)
    except:
        return {"msg": "Gagal memanggil data dari database"}, 500

    return {"histories": histories}, 200


"""
------------------------------------------------------------------------------
Mendelete history
------------------------------------------------------------------------------
"""


@bp.route("/detail-history/<history_id>", methods=['DELETE', 'PUT', 'GET'])
@jwt_required
def delete_history(history_id):
    claims = get_jwt_claims()
    if not ObjectId.is_valid(history_id):
        return {"msg": "Object ID tidak valid"}, 400

    if request.method == 'GET':
        try:
            history = history2_query.get_history(history_id)
        except:
            return {"msg": "Gagal memanggil data dari database"}, 500

        return jsonify(history), 200

    if request.method == 'PUT':
        schema = HistoryEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        category_available = ["PC", "CCTV", "DAILY", "HANDHELD"]
        if data["category"].upper() not in category_available:
            return {"msg": "Category tidak valid!"}, 400

        start_date = data["date"]
        if not data["end_date"]:
            end_date = None
            duration = 0
        else:
            end_date = data["end_date"]
            time_delta = end_date - start_date
            total_second = time_delta.total_seconds()
            duration = int(total_second / 60)

        edit_dto = EditHistoryDto2(
            filter_id=history_id,
            filter_branch=claims["branch"],
            filter_timestamp=data["timestamp"],

            location=data["location"],
            status=data["status"],
            date=data["date"],
            end_date=end_date,
            note=data["note"],
            duration=duration,
            resolve_note=data["resolve_note"],
            complete_status=data["complete_status"],
            updated_by=claims["name"],
            updated_by_id=get_jwt_identity(),
        )

        try:
            history = history2_update.update_history(edit_dto)
        except:
            return {"msg": "Gagal memanggil data dari database"}, 500

        if history is None:
            return {"msg": "Gagal memperbarui riwayat, kesalahan pada cabang atau timestamp"}, 400

        # Jika history complete_status 2 (komplete) maka berarti harus dihapus di parrentnya
        if history["complete_status"] == 2:
            if history["category"] == "PC":
                parent = computer_update.delete_case_computer(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )
                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

            if history["category"] == "CCTV":
                parent = cctv_update.delete_case_cctv(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )

                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

            if history["category"] == "HANDHELD":
                parent = handheld_update.delete_case_handheld(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )
                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

        # Jika history complete_status != 2 (tidak komplete) maka berarti
        # harus dihapus lalu ditambahkan lagi di parrentnya
        else:
            case = f'{data["status"]} : {data["note"]}'
            if data["complete_status"] == 1:
                case = f'##PENDING## {data["status"]} : {data["note"]}'

            if history["category"] == "PC":
                parent = computer_update.delete_case_computer(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )
                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

                computer_update.insert_case_computer(
                    history["parent_id"],
                    claims["branch"],
                    str(history_id),
                    case
                )

            if history["category"] == "CCTV":
                parent = cctv_update.delete_case_cctv(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )

                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

                cctv_update.insert_case_cctv(
                    history["parent_id"],
                    claims["branch"],
                    str(history_id),
                    case
                )

            if history["category"] == "HANDHELD":
                parent = handheld_update.delete_case_handheld(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )
                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

                handheld_update.insert_case_handheld(
                    history["parent_id"],
                    claims["branch"],
                    str(history_id),
                    case
                )

        return jsonify(history), 200

    if request.method == 'DELETE':

        # dua jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=24)

        try:
            history = history2_update.delete_history(history_id, claims["branch"], time_limit)
        except:
            return {"msg": "Gagal memanggil data dari database"}, 500
        if history is None:
            return {"msg": "Gagal menghapus riwayat, batas waktu 24 jam telah tercapai !"}, 400

        # Jika history belum komplete, berarti harus dihapus di parrentnya karena masih nyantol
        if history["complete_status"] < 2:
            if history["category"] == "PC":
                parent = computer_update.delete_case_computer(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )
                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

            if history["category"] == "CCTV":
                parent = cctv_update.delete_case_cctv(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )

                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

            if history["category"] == "HANDHELD":
                parent = handheld_update.delete_case_handheld(
                    history["parent_id"],
                    claims["branch"],
                    history_id,
                )
                if parent is None:
                    return {"msg": "Case pada parent tidak terhapus"}, 500

        return {"msg": "history berhasil dihapus"}, 204


@bp.route("/histories-progress-count", methods=['GET'])
@jwt_required
def get_history_progress_count():
    branch = ""
    if request.args.get("branch"):
        branch = request.args.get("branch")

    try:
        progress_count = history2_query.get_histories_in_progress_count(branch)
    except:
        return {"msg": "Gagal memanggil data dari database"}, 500

    return {"issues": progress_count}, 200


@bp.route("/history-dashboard", methods=['GET'])
@jwt_required
def get_history_for_dashboard():
    branch = ""
    if request.args.get("branch"):
        branch = request.args.get("branch")

    progress_count = history2_query.get_histories_in_progress_count(branch)
    histories = history2_query.find_histories_by_branch_by_category(branch, "", -1, 3)
    option_lvl = options_json_object["version"]

    return {"issues": progress_count, "histories": histories, "option_lvl": option_lvl}, 200
