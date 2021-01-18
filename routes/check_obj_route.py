from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
)
from marshmallow import ValidationError

from config import config as cf
from dao import (cctv_query,
                 cctv_update,
                 history2_update)
from dto.cctv_dto import CctvDto, CctvEditDto, CctvChangeActiveDto
from dto.history2_dto import HistoryDto2
from input_schemas.cctv import (CctvInsertSchema, CctvEditSchema, CctvAppendStatusSchema, CctvChangeActiveSchema)
from validations.input_validation import is_ip_address_valid
from validations.role_validation import is_end_user

bp = Blueprint('check_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
List cctv localhost:5001/cctv?branch=&ip_address=?cctv_name=?deactive=
dan Membuat Cctv
------------------------------------------------------------------------------
"""


@bp.route("/check", methods=['GET', 'POST'])
def find_cctv():
    if request.method == 'GET':
        branch = "BANJARMASIN" #claims["branch"]
        if request.args.get("branch"):
            branch = request.args.get("branch")

        cctvs = cctv_query.find_cctv_must_check(branch=branch, )

        return {"cctvs": cctvs}, 200
