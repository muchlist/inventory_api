from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
)
from marshmallow import ValidationError

from dao import (handheld_query,
                 handheld_update,
                 history_update)
from dto.handheld_dto import HandheldDto, HandheldEditDto, HandheldChangeActiveDto
from dto.history_dto import HistoryDto
from input_schemas.handheld import (HandheldInsertSchema,
                                    HandheldEditSchema,
                                    HandheldChangeActiveSchema)
from validations.role_validation import is_end_user

bp = Blueprint('handheld_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
List handheld localhost:5001/handhelds?branch=&handheld_name=?deactive=
dan Membuat handheld
------------------------------------------------------------------------------
"""


@bp.route("/handhelds", methods=['GET', 'POST'])
@jwt_required
def find_handhelds():
    claims = get_jwt_claims()

    if request.method == 'POST':

        schema = HandheldInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": f"{str(err)}"}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        handheld_dto = HandheldDto(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            handheld_name=data["handheld_name"],
            phone=data["phone"],
            ip_address=data["ip_address"],
            inventory_number=data["inventory_number"],
            author=claims["name"],
            branch=claims["branch"],
            location=data["location"],
            year=data["year"],
            merk=data["merk"],
            tipe=data["tipe"],
            last_status="INIT",
            note=data["note"],
            deactive=data["deactive"],
        )

        try:
            result = handheld_update.create_handheld(handheld_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':
        handheld_name = request.args.get("handheld_name")
        deactive = request.args.get("deactive")
        branch = claims["branch"]
        location = request.args.get("location")

        if request.args.get("branch"):
            branch = request.args.get("branch")

        handhelds = handheld_query.find_handheld_by_branch_handheld_name(
            branch, location, handheld_name, deactive)

        return {"handhelds": handhelds}, 200


"""
------------------------------------------------------------------------------
Detail handheld localhost:5001/handhelds/objectID
------------------------------------------------------------------------------
"""


@bp.route("/handhelds/<handheld_id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def detail_computers(handheld_id):
    if not ObjectId.is_valid(handheld_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'GET':

        try:
            handheld = handheld_query.get_handheld(handheld_id)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if handheld is None:
            return {"msg": "Handheld dengan ID tersebut tidak ditemukan"}, 400

        return jsonify(handheld), 200

    if request.method == 'PUT':
        schema = HandheldEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        handheld_edit_dto = HandheldEditDto(
            filter_id=handheld_id,
            filter_timestamp=data["timestamp"],
            filter_branch=claims["branch"],

            updated_at=datetime.now(),
            handheld_name=data["handheld_name"],
            phone=data["phone"],
            ip_address=data["ip_address"],
            inventory_number=data["inventory_number"],
            author=claims["name"],
            location=data["location"],
            year=data["year"],
            merk=data["merk"],
            tipe=data["tipe"],
            note=data["note"],
            deactive=data["deactive"],
        )

        try:
            result = handheld_update.update_handheld(handheld_edit_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        if result is None:
            return {"msg": "Kesalahan pada ID, Cabang, atau sudah ada perubahan sebelumnya"}, 400

        history_dto = HistoryDto(result["_id"],
                                 result["handheld_name"],
                                 "Handheld",
                                 claims["name"],
                                 result["branch"],
                                 "EDITED",
                                 "Detail handheld dirubah",
                                 datetime.now(),
                                 get_jwt_identity(),
                                 )
        history_update.insert_history(history_dto)

        return jsonify(result), 200

    if request.method == 'DELETE':

        # dua jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=2)

        try:
            handheld = handheld_update.delete_handheld(
                handheld_id, claims["branch"], time_limit)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if handheld is None:
            return {"msg": "Gagal menghapus handheld, batas waktu dua jam telah tercapai !"}, 400

        return {"msg": "Handheld berhasil di hapus"}, 204


"""
------------------------------------------------------------------------------
Change Status active handheld localhost:5001/handhelds/objectID/active
------------------------------------------------------------------------------
"""


@bp.route("/handhelds/<handheld_id>/<active_status>", methods=['POST'])
@jwt_required
def change_activate_handhelds(handheld_id, active_status):
    if not ObjectId.is_valid(handheld_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'POST':

        schema = HandheldChangeActiveSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if active_status.upper() not in ["ACTIVE", "DEACTIVE"]:
            return {"msg": "Input tidak valid, ACTIVE, DEACTIVE"}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        change_active_dto = HandheldChangeActiveDto(
            filter_id=handheld_id,
            filter_timestamp=data["timestamp"],
            filter_branch=claims["branch"],
            updated_at=datetime.now(),
            deactive=active_status.upper() == "DEACTIVE"
        )

        try:
            handheld = handheld_update.change_activate_handheld(change_active_dto)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if handheld is None:
            return {"msg": "Kesalahan pada ID, Cabang, atau sudah ada perubahan sebelumnya"}, 400

        return jsonify(handheld), 200
