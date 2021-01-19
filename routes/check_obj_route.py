from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (check_obj_update,
                 check_obj_query)
from dto.check_obj_dto import CheckObjDto, EditCheckObjDto
from input_schemas.check_obj import (CheckObjInsertSchema, CheckObjEditSchema)
from validations.role_validation import is_end_user

bp = Blueprint('check_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
List check object localhost:5001/check-obj?branch=&name=?
------------------------------------------------------------------------------
"""


@bp.route("/check-obj", methods=['GET', 'POST'])
@jwt_required
def find_check():
    claims = get_jwt_claims()

    if request.method == 'POST':
        schema = CheckObjInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        check_dto = CheckObjDto(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name=data["name"],
            branch=claims["branch"],
            location=data["location"],
            type=data["type"],
            last_status="",
            note=data["note"]
        )

        try:
            result = check_obj_update.create_check_obj(check_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':
        name = request.args.get("name")
        obj_type = request.args.get("obj_type")
        check_obj = check_obj_query.find_check_obj(branch=claims["branch"],
                                                   name=name,
                                                   obj_type=obj_type)

        return {"check-obj": check_obj}, 200


"""
------------------------------------------------------------------------------
Detail Cctv localhost:5001/cctvs/objectID
------------------------------------------------------------------------------
"""


@bp.route("/check-obj/<id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def detail_check_obj(id):
    if not ObjectId.is_valid(id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'GET':

        try:
            check = check_obj_query.get_check_obj(id)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if check is None:
            return {"msg": "Cctv dengan ID tersebut tidak ditemukan"}, 404

        return jsonify(check), 200

    if request.method == 'PUT':
        schema = CheckObjEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        check_obj_edit_dto = EditCheckObjDto(
            filter_id=id,
            filter_branch=claims["branch"],

            branch=claims["branch"],
            updated_at=datetime.now(),
            name=data["name"],
            location=data["location"],
            note=data["note"],
            type=data["type"]
        )

        try:
            result = check_obj_update.update_check_obj(check_obj_edit_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 200

    if request.method == 'DELETE':

        try:
            check_obj = check_obj_update.delete_check_obj(
                id, claims["branch"], )
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if check_obj is None:
            return {"msg": "Gagal menghapus check objek!"}, 400

        return {"msg": "check objek berhasil di hapus"}, 204
