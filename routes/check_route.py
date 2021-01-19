from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (check_obj_update,
                 check_obj_query, cctv_query, check_update, check_query)
from dto.check_dto import CheckDto, CheckObjEmbedDto
from dto.check_obj_dto import CheckObjDto, EditCheckObjDto
from input_schemas.check import CheckInsertSchema
from input_schemas.check_obj import (CheckObjInsertSchema, CheckObjEditSchema)
from validations.role_validation import is_end_user

bp = Blueprint('checklist_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
List check object localhost:5001/check-obj?branch=&name=?
------------------------------------------------------------------------------
"""


@bp.route("/check", methods=['GET', 'POST'])
@jwt_required
def find_check():
    claims = get_jwt_claims()

    if request.method == 'POST':
        schema = CheckInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        obj_embed_list = []
        check_obj_list = check_obj_query.find_check_obj(claims["branch"], "", "")
        for obj in check_obj_list:
            obj_embed = CheckObjEmbedDto(
                id=obj["_id"],
                name=obj["name"],
                is_checked=False,
                checked_at=None,
                checked_note="",
                is_resolve=False,
                location=obj["location"],
                type=obj["type"],
                image_path="",
            )._asdict()
            obj_embed_list.append(obj_embed)

        check_obj_cctv = cctv_query.find_cctv_must_check(claims["branch"])
        for cctv in check_obj_cctv:
            obj_cctv = CheckObjEmbedDto(
                id=cctv["_id"],
                name=cctv["cctv_name"],
                is_checked=False,
                checked_at=None,
                checked_note="",
                is_resolve=False,
                location=cctv["location"],
                type="CCTV",
                image_path="",
            )._asdict()
            obj_embed_list.append(obj_cctv)

        check_dto = CheckDto(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=claims["name"],
            branch=claims["branch"],
            is_finish=False,
            shift=data["shift"],
            checks_obj=obj_embed_list
        )

        try:
            result = check_update.create_check(check_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':
        check = check_query.find_check(branch=claims["branch"],)

        return {"check": check}, 200
