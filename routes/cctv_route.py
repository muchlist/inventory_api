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
                 history_update)
from dto.cctv_dto import CctvDto, CctvEditDto, CctvChangeActiveDto
from dto.history_dto import HistoryDto
from input_schemas.cctv import (CctvInsertSchema, CctvEditSchema, CctvAppendStatusSchema, CctvChangeActiveSchema)
from validations.input_validation import is_ip_address_valid
from validations.role_validation import is_end_user

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
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
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
        location = request.args.get("location")
        last_ping = request.args.get("last_ping")
        branch = claims["branch"]

        if request.args.get("branch"):
            branch = request.args.get("branch")

        cctvs = cctv_query.find_cctv_by_branch_ip_cctv_name(
            branch=branch,
            location=location,
            ip_address=ip_address,
            cctv_name=cctv_name,
            last_ping=last_ping,
            deactive=deactive)

        return {"cctvs": cctvs}, 200


"""
------------------------------------------------------------------------------
Detail Cctv localhost:5001/cctvs/objectID
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
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
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
                                 datetime.now(),
                                 get_jwt_identity(),
                                 )
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
            return {"msg": "Gagal menghapus cctv, batas waktu dua jam telah tercapai !"}, 400

        return {"msg": "cctv berhasil di hapus"}, 204


"""
------------------------------------------------------------------------------
Append Status CCTV localhost:5001/cctvs/append
------------------------------------------------------------------------------
"""


@bp.route("/cctv-states-update", methods=['POST'])
def append_cctv_ping_state():
    if request.method == 'POST':

        key = request.args.get("key")
        if key != cf.get('cctv_secret_key'):
            return {"msg": "Key tidak valid"}, 400

        schema = CctvAppendStatusSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        response_code = cctv_update.append_status_ping_cctv(data["ip_addresses"], data["ping_code"])
        if response_code == 400:
            return {"msg": "Update gagal"}, 400
        return {"msg": "Success"}, 200


@bp.route("/cctv-ip", methods=['GET'])
def cctv_ip_list():
    if request.method == 'GET':

        key = request.args.get("key")
        branch = request.args.get("branch")
        location = request.args.get("location")

        if key != cf.get('cctv_secret_key'):
            return {"msg": "Key tidak valid"}, 400

        if branch is None:
            return {"msg": "Argumen cabang tidak valid"}, 400

        cctv_ip_address = cctv_query.find_cctv_ip_list(branch, location)
        return {"cctv_ip": cctv_ip_address}, 200


"""
------------------------------------------------------------------------------
Change Status active komputer localhost:5001/computers/objectID/active
------------------------------------------------------------------------------
"""


@bp.route("/cctvs/<cctv_id>/<active_status>", methods=['POST'])
@jwt_required
def change_activate_cctv(cctv_id, active_status):
    if not ObjectId.is_valid(cctv_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'POST':

        schema = CctvChangeActiveSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if active_status.upper() not in ["ACTIVE", "DEACTIVE"]:
            return {"msg": "Input tidak valid, ACTIVE, DEACTIVE"}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        change_active_dto = CctvChangeActiveDto(
            filter_id=cctv_id,
            filter_timestamp=data["timestamp"],
            filter_branch=claims["branch"],
            updated_at=datetime.now(),
            deactive=active_status.upper() == "DEACTIVE"
        )

        try:
            computer = cctv_update.change_activate_cctv(change_active_dto)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if computer is None:
            return {"msg": "Kesalahan pada ID, Cabang, atau sudah ada perubahan sebelumnya"}, 400

        return jsonify(computer), 200
