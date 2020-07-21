from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (cctv_query,
                 cctv_update,
                 history_update)
from dto.cctv_dto import CctvDto, CctvEditDto
from dto.history_dto import HistoryDto
from input_schemas.cctv import (CctvInsertSchema, CctvEditSchema)
from validations.input_validation import is_ip_address_valid
from validations.role_validation import isEndUser

bp = Blueprint('cctv_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
List cctv localhost:5001/cctv?branch=&ip_address=?cctv_name=?deactive=
dan Membuat Cctv
------------------------------------------------------------------------------
"""


@bp.route("/cctvs", methods=['GET', 'POST'])
@jwt_required
def find_cctv():
    claims = get_jwt_claims()

    if request.method == 'POST':

        schema = CctvInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            # return err.messages, 400
            return {"msg": "Input tidak valid"}, 400

        if not isEndUser(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400
        if not is_ip_address_valid(data["ip_address"]):
            return {"msg": "IP Address salah"}, 400

        cctv_dto = CctvDto(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            cctv_name=data["cctv_name"],
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
            ping_state=[]
        )

        try:
            result = cctv_update.create_cctv(cctv_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':
        ip_address = request.args.get("ip_address")
        cctv_name = request.args.get("cctv_name")
        deactive = request.args.get("deactive")
        branch = claims["branch"]

        if request.args.get("branch"):
            branch = request.args.get("branch")

        cctvs = cctv_query.find_cctv_by_branch_ip_cctv_name(
            branch, ip_address, cctv_name, deactive)

        return {"cctvs": cctvs}, 200


"""
------------------------------------------------------------------------------
Detail komputer localhost:5001/computers/objectID
------------------------------------------------------------------------------
"""


@bp.route("/cctvs/<cctv_id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def detail_cctvs(cctv_id):
    if not ObjectId.is_valid(cctv_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'GET':

        try:
            cctv = cctv_query.get_cctv(cctv_id)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if cctv is None:
            return {"msg": "Cctv dengan ID tersebut tidak ditemukan"}, 404

        return jsonify(cctv), 200

    if request.method == 'PUT':
        schema = CctvEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            # return err.messages, 400
            return {"msg": "Input tidak valid"}, 400

        if not isEndUser(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400
        if not is_ip_address_valid(data["ip_address"]):
            return {"msg": "IP Address salah"}, 400

        data["score"] = 0

        cctv_edit_dto = CctvEditDto(
            filter_id=cctv_id,
            filter_timestamp=data["timestamp"],
            filter_branch=claims["branch"],

            updated_at=datetime.now(),
            cctv_name=data["cctv_name"],
            ip_address=data["ip_address"],
            inventory_number=data["inventory_number"],
            author=claims["name"],
            location=data["location"],
            year=data["year"],
            merk=data["merk"],
            tipe=data["tipe"],
            note=data["note"],
            deactive=data["deactive"]
        )

        try:
            result = cctv_update.update_cctv(cctv_edit_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        if result is None:
            return {"msg": "gagal update komputer, data telah diubah oleh orang lain sebelumnya"}, 400

        history_dto = HistoryDto(result["_id"],
                                 result["cctv_name"],
                                 "CCTV",
                                 claims["name"],
                                 result["branch"],
                                 "EDITED",
                                 "Detail cctv dirubah",
                                 datetime.now())
        history_update.insert_history(history_dto)

        return jsonify(result), 200

    if request.method == 'DELETE':

        # dua jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=2)

        try:
            cctv = cctv_update.delete_cctv(
                cctv_id, claims["branch"], time_limit)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if cctv is None:
            return {"msg": "gagal menghapus cctv, hanya dapat dihapus dua jam setelah pembuatan"}, 400

        return {"msg": "cctv berhasil di hapus"}, 204
