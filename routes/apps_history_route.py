from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
)
from marshmallow import ValidationError

from dao import (apps_histo_query,
                 apps_histo_update,
                 apps_update,
                 history_update)
from dto.apps_histo_dto import AppsHistoDto, AppsEditHistoDto
from dto.history_dto import HistoryDto
from input_schemas.apps_history import (AppsHistoryInsertSchema, AppsHistoryEditSchema)

bp = Blueprint('apps_history_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
Membuat dan mengambil Histories per parent
------------------------------------------------------------------------------
"""


@bp.route("/apps/<parent_id>/histories", methods=['GET', 'POST'])
@jwt_required
def apps_history_per_parent(parent_id):
    claims = get_jwt_claims()

    if request.method == 'POST':
        schema = AppsHistoryInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not ObjectId.is_valid(parent_id):
            return {"msg": "Object ID tidak valid"}, 400

        increment_counter = 0
        if data["is_complete"]:
            increment_counter = 1

        parent_apps = apps_update.increment_counter(parent_id, increment_counter)
        if parent_apps is None:
            return {"msg": "Kesalahan pada ID Aplikasi"}, 400

        start_date = data["start_date"]

        if "end_date" in data:
            end_date = data["end_date"]
            time_delta = end_date - start_date
            total_second = time_delta.total_seconds()
            duration = int(total_second / 60)
        else:
            end_date = None
            duration = 0

        # if not data["end_date"]:
        #     end_date = None
        #     duration = 0
        # else:
        #     end_date = data["end_date"]
        #     time_delta = end_date - start_date
        #     total_second = time_delta.total_seconds()
        #     duration = int(total_second / 60)

        apps_history_dto = AppsHistoDto(
            author=claims["name"],
            author_id=get_jwt_identity(),
            branch=claims["branch"],
            location=data["location"],
            status=data["status"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            start_date=start_date,
            end_date=end_date,
            title=data["title"],
            desc=data["desc"],
            parent_id=parent_id,
            parent_name=parent_apps["apps_name"],
            duration=duration,
            resolve_note=data["resolve_note"],
            pic=data["pic"],
            is_complete=data["is_complete"],
        )

        try:
            history_id = apps_histo_update.insert_apps_history(apps_history_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        # Menambahkan simple history jika is_complete
        if data["is_complete"]:
            note = f"prob: {data['title']}\nsolu: {data['resolve_note']}"
            history_dto = HistoryDto(history_id,
                                     parent_apps["apps_name"],
                                     "APPLICATION",
                                     claims["name"],
                                     claims["branch"],
                                     data["status"],
                                     note,
                                     datetime.now(),
                                     get_jwt_identity(),
                                     )
            history_update.insert_history(history_dto)

        return {"msg": f"Berhasil menambahkan riwayat aplikasi dengan id {history_id}"}, 201

    # GET HISTORY APP PER APP
    if request.method == 'GET':
        if not ObjectId.is_valid(parent_id):
            return {"msg": "Object ID tidak valid"}, 400
        try:
            histories = apps_histo_query.find_apps_history_for_parent_app(parent_id)
        except:
            return {"msg": "Gagal memanggil data dari database"}, 500

        return {"histories": histories}, 200


"""
------------------------------------------------------------------------------
mengambil history aplikasi per cabang dan per kategory
api.com/apps-histories?category=Jaringan&branch=BANJARMASIN
------------------------------------------------------------------------------
"""


@bp.route("/apps-histories", methods=['GET'])
@jwt_required
def find_apps_history():
    app_name = request.args.get("app_name")
    branch = request.args.get("branch")
    status = request.args.get("status")
    limit = request.args.get("limit")
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return {"msg": "limit harus berupa angka"}, 400

    try:
        histories = apps_histo_query.find_histories_by_name_branch_category(app_name, branch, status, limit)
    except:
        return {"msg": "Gagal memanggil data dari database"}, 500

    return {"histories": histories}, 200


"""
------------------------------------------------------------------------------
Detail, update dan delete history app
------------------------------------------------------------------------------
"""


@bp.route("/app-histories/<history_id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def detail_apps_history(history_id):
    claims = get_jwt_claims()

    if not ObjectId.is_valid(history_id):
        return {"msg": "Object ID tidak valid"}, 400

    if request.method == 'GET':
        try:
            apps_histo = apps_histo_query.get_apps_history(history_id)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if apps_histo is None:
            return {"msg": "Riwayat dengan ID tersebut tidak ditemukan"}, 404

        return jsonify(apps_histo), 200

    if request.method == 'PUT':
        schema = AppsHistoryEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        start_date = data["start_date"]
        if not data["end_date"]:
            end_date = None
            duration = 0
        else:
            end_date = data["end_date"]
            time_delta = end_date - start_date
            total_second = time_delta.total_seconds()
            duration = int(total_second / 60)

        edit_apps_history_dto = AppsEditHistoDto(
            filter_id=history_id,
            filter_branch=claims["branch"],
            filter_timestamp=data["timestamp"],

            author=claims["name"],
            author_id=get_jwt_identity(),
            branch=claims["branch"],
            location=data["location"],
            status=data["status"],
            start_date=start_date,
            end_date=end_date,
            title=data["title"],
            desc=data["desc"],
            duration=duration,
            resolve_note=data["resolve_note"],
            pic=data["pic"],
            is_complete=data["is_complete"],
        )

        try:
            history_app = apps_histo_update.update_apps_histo(edit_apps_history_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        if history_app is None:
            return {"msg": "Kesalahan pada ID, Cabang, atau sudah ada perubahan sebelumnya"}, 400

        # Menambahkan counter pada parent
        if data["is_complete"]:
            apps_update.increment_counter(history_app["parent_id"], 1)

        # Menambahkan simple history jika is_complete
        if data["is_complete"]:
            note = f"prob: {data['title']}\nsolu: {data['resolve_note']}"
            history_dto = HistoryDto(history_id,
                                     history_app["parent_name"],
                                     "APPLICATION",
                                     claims["name"],
                                     claims["branch"],
                                     data["status"],
                                     note,
                                     datetime.now(),
                                     get_jwt_identity(),
                                     )
            history_update.insert_history(history_dto)

        return jsonify(history_app), 200

    if request.method == 'DELETE':
        # dua jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=2)

        try:
            history = apps_histo_update.delete_apps_history(history_id, claims["branch"], time_limit)
        except:
            return {"msg": "Gagal memanggil data dari database"}, 500
        if history is None:
            return {"msg": "Gagal menghapus riwayat, batas waktu dua jam telah tercapai !"}, 400

        apps_update.increment_counter(history["parent_id"], -1)

        return {"msg": "history berhasil dihapus"}, 204
