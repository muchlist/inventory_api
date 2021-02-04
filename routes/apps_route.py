from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (apps_query,
                 apps_update)
from dto.apps_dto import (AppsDto, AppsEditDto)
from input_schemas.apps import (AppsInsertSchema, AppsEditSchema, )
from validations.role_validation import is_end_user

bp = Blueprint('apps_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
List apps localhost:5001/apps?apps_name=""
dan Membuat Apps
------------------------------------------------------------------------------
"""


@bp.route("/apps", methods=['GET', 'POST'])
@jwt_required
def find_apps():
    claims = get_jwt_claims()

    if request.method == 'POST':

        schema = AppsInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        apps_dto = AppsDto(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            apps_name=data["apps_name"],
            description=data["description"],
            branches=data["branches"],
            programmers=data["programmers"],
            url=data["url"],
            platform=data["platform"],
            note=data["note"],
        )

        try:
            result = apps_update.create_apps(apps_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':
        apps_name = request.args.get("apps_name")

        apps = apps_query.find_apps_and_filter(
            apps_name=apps_name,
            branch=claims["branch"],
        )

        return {"apps": apps}, 200


"""
------------------------------------------------------------------------------
Detail Apps localhost:5001/apps/objectID
------------------------------------------------------------------------------
"""


@bp.route("/apps/<apps_id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def detail_apps(apps_id):
    if not ObjectId.is_valid(apps_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'GET':

        try:
            apps = apps_query.get_apps(apps_id)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if apps is None:
            return {"msg": "Aplikasi dengan ID tersebut tidak ditemukan"}, 404

        return jsonify(apps), 200

    if request.method == 'PUT':
        schema = AppsEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        apps_edit_dto = AppsEditDto(
            filter_id=apps_id,
            filter_timestamp=data["timestamp"],

            updated_at=datetime.now(),
            apps_name=data["apps_name"],
            description=data["description"],
            branches=data["branches"],
            programmers=data["programmers"],
            url=data["url"],
            platform=data["platform"],
            note=data["note"],
        )

        try:
            result = apps_update.update_apps(apps_edit_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        if result is None:
            return {"msg": "gagal update aplikasi, data telah diubah oleh orang lain sebelumnya"}, 400

        return jsonify(result), 200

    if request.method == 'DELETE':

        # dua jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=24)

        try:
            apps = apps_update.delete_apps(
                apps_id, time_limit)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if apps is None:
            return {"msg": "Gagal menghapus aplikasi, batas waktu 24 jam telah tercapai !"}, 400

        return {"msg": "Aplikasi berhasil di hapus"}, 204
