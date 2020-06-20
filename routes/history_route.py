from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    get_jwt_claims,
)
from input_schemas.history import (HistoryInsertSchema)
from dao import (history_query,
                 history_update)
from dto.history_dto import HistoryDto

from datetime import datetime

bp = Blueprint('history_bp', __name__, url_prefix='/api')


"""
------------------------------------------------------------------------------

------------------------------------------------------------------------------
"""
@bp.route("/histories", methods=['GET', 'POST'])
@jwt_required
def insert_history(name):

    claims = get_jwt_claims()

    if request.method == 'POST':
        schema = HistoryInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if data["time"] is not None:
            data["time"] = datetime.now()

        history_dto = HistoryDto(data["parent_id"],
                                 data["category"],
                                 claims["name"],
                                 claims["branch"],
                                 data["status"],
                                 data["note"],
                                 datetime.now())

        try:
            history_update.insert_history(history_dto)
        except:
            return {"message": "Gagal menyimpan data ke database"}, 500
        return {"message": "history berhasil dimasukkan"}, 201

    if request.method == 'GET':
        return {"message": "implement me"}, 200
