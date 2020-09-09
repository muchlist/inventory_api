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
                 apps_query)
from dto.apps_histo_dto import AppsHistoDto, AppsEditHistoDto
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

        parent_apps = apps_query.get_apps(parent_id)
        if parent_apps is None:
            return {"msg": "Kesalahan pada ID Aplikasi"}, 400

        start_date = data["start_date"]
        end_date = data["end_date"]
        time_delta = end_date - start_date
        total_second = time_delta.total_seconds()
        duration = int(total_second / 60)

        apps_history_dto = AppsHistoDto(
            author=claims["name"],
            author_id=get_jwt_identity(),
            branch=claims["branch"],
            location=data["location"],
            category=data["category"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            start_date=start_date,
            end_date=end_date,
            title=data["title"],
            desc=data["desc"],
            parent_id=parent_id,
            parent_name=parent_apps["apps_name"],
            duration=duration
        )

        try:
            history_id = apps_histo_update.insert_apps_history(apps_history_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

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
    category = request.args.get("category")
    limit = request.args.get("limit")
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return {"msg": "limit harus berupa angka"}, 400

    try:
        histories = apps_histo_query.find_histories_by_name_branch_category(app_name, branch, category, limit)
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
            return {"msg": "Cctv dengan ID tersebut tidak ditemukan"}, 404

        return jsonify(apps_histo), 200

    if request.method == 'PUT':
        schema = AppsHistoryEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        start_date = data["start_date"]
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
            category=data["category"],
            start_date=start_date,
            end_date=end_date,
            title=data["title"],
            desc=data["desc"],
            duration=duration
        )

        try:
            history = apps_histo_update.update_apps_histo(edit_apps_history_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        if history is None:
            return {"msg": "Kesalahan pada ID, Cabang, atau sudah ada perubahan sebelumnya"}, 400

        return jsonify(history), 200

    if request.method == 'DELETE':
        # dua jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=2)

        try:
            history = apps_histo_update.delete_apps_history(history_id, claims["branch"], time_limit)
        except:
            return {"msg": "Gagal memanggil data dari database"}, 500
        if history is None:
            return {"msg": "Gagal menghapus riwayat, batas waktu dua jam telah tercapai !"}, 400

        return {"msg": "history berhasil dihapus"}, 204
