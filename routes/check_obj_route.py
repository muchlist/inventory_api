from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (check_obj_update,
                 check_obj_query)
from dto.check_obj_dto import CheckObjDto
from input_schemas.check_obj import (CheckObjInsertSchema)
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
