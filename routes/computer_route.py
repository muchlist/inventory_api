from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
)
from marshmallow import ValidationError

from dao import (computer_query,
                 computer_update,
                 history2_update)
from dto.computer_dto import ComputerDto, SpecDto, ComputerEditDto, ComputerChangeActiveDto
from dto.history2_dto import HistoryDto2
from input_schemas.computer import (ComputerInsertSchema,
                                    ComputerEditSchema,
                                    ComputerChangeActiveSchema)
from validations.input_validation import is_ip_address_valid
from validations.role_validation import is_end_user

bp = Blueprint('computer_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
List komputer localhost:5001/computers?branch=&ip_address=?client_name=?deactive=
dan Membuat Komputer
------------------------------------------------------------------------------
"""


@bp.route("/computers", methods=['GET', 'POST'])
@jwt_required
def find_computers():
    claims = get_jwt_claims()

    if request.method == 'POST':

        schema = ComputerInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400
        if not is_ip_address_valid(data["ip_address"]):
            return {"msg": "IP Address salah"}, 400

        spec_dto = SpecDto(
            processor=data["processor"],
            ram=data["ram"],
            hardisk=data["hardisk"],
            score=0,
        )

        computer_dto = ComputerDto(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            client_name=data["client_name"],
            hostname=data["hostname"],
            ip_address=data["ip_address"],
            inventory_number=data["inventory_number"],
            author=claims["name"],
            branch=claims["branch"],
            location=data["location"],
            division=data["division"],
            seat_management=data["seat_management"],
            year=data["year"],
            merk=data["merk"],
            tipe=data["tipe"],
            operation_system=data["operation_system"],
            last_status="INIT",
            note=data["note"],
            deactive=data["deactive"],
            spec=spec_dto
        )

        try:
            result = computer_update.create_computer(computer_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':
        ip_address = request.args.get("ip_address")
        client_name = request.args.get("client_name")
        deactive = request.args.get("deactive")
        seat = request.args.get("seat")
        branch = claims["branch"]
        location = request.args.get("location")
        division = request.args.get("division")

        if request.args.get("branch"):
            branch = request.args.get("branch")

        computers = computer_query.find_computer_by_branch_ip_clientname(
            branch, ip_address, client_name, location, division, seat, deactive)

        return {"computers": computers}, 200


"""
------------------------------------------------------------------------------
Detail komputer localhost:5001/computers/objectID
------------------------------------------------------------------------------
"""


@bp.route("/computers/<computer_id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def detail_computers(computer_id):
    if not ObjectId.is_valid(computer_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'GET':

        try:
            computer = computer_query.get_computer(computer_id)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if computer is None:
            return {"msg": "Komputer dengan ID tersebut tidak ditemukan"}, 400

        return jsonify(computer), 200

    if request.method == 'PUT':
        schema = ComputerEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            # return err.messages, 400
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400
        if not is_ip_address_valid(data["ip_address"]):
            return {"msg": "IP Address salah"}, 400

        data["score"] = 0

        spec_dto = SpecDto(
            processor=data["processor"],
            ram=data["ram"],
            hardisk=data["hardisk"],
            score=data["score"],
        )

        computer_edit_dto = ComputerEditDto(
            filter_id=computer_id,
            filter_timestamp=data["timestamp"],
            filter_branch=claims["branch"],

            updated_at=datetime.now(),
            client_name=data["client_name"],
            hostname=data["hostname"],
            ip_address=data["ip_address"],
            inventory_number=data["inventory_number"],
            author=claims["name"],
            location=data["location"],
            division=data["division"],
            seat_management=data["seat_management"],
            year=data["year"],
            merk=data["merk"],
            tipe=data["tipe"],
            operation_system=data["operation_system"],
            note=data["note"],
            deactive=data["deactive"],
            spec=spec_dto,
        )

        try:
            result = computer_update.update_computer(computer_edit_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        if result is None:
            return {"msg": "Kesalahan pada ID, Cabang, atau sudah ada perubahan sebelumnya"}, 400

        history2_dto = HistoryDto2(author=claims["name"],
                                   author_id=get_jwt_identity(),
                                   branch=claims["branch"],
                                   category="PC",
                                   location=data["location"],
                                   status="EDITED",
                                   date=datetime.now(),
                                   end_date=datetime.now(),
                                   note="Detail PC dirubah",
                                   duration=0,
                                   resolve_note="",
                                   is_complete=True,
                                   created_at=datetime.now(),
                                   parent_id=result["_id"],
                                   parent_name=result["client_name"],
                                   updated_by=claims["name"],
                                   updated_by_id=get_jwt_identity(),
                                   timestamp=datetime.now(),
                                   )

        history2_update.insert_history(ObjectId(), history2_dto)

        return jsonify(result), 200

    if request.method == 'DELETE':

        # dua jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=24)

        try:
            computer = computer_update.delete_computer(
                computer_id, claims["branch"], time_limit)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if computer is None:
            return {"msg": "Gagal menghapus komputer, batas waktu 24 jam telah tercapai !"}, 400

        return {"msg": "komputer berhasil di hapus"}, 204


"""
------------------------------------------------------------------------------
Change Status active komputer localhost:5001/computers/objectID/active
------------------------------------------------------------------------------
"""


@bp.route("/computers/<computer_id>/<active_status>", methods=['POST'])
@jwt_required
def change_activate_computers(computer_id, active_status):
    if not ObjectId.is_valid(computer_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'POST':

        schema = ComputerChangeActiveSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if active_status.upper() not in ["ACTIVE", "DEACTIVE"]:
            return {"msg": "Input tidak valid, ACTIVE, DEACTIVE"}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        change_active_dto = ComputerChangeActiveDto(
            filter_id=computer_id,
            filter_timestamp=data["timestamp"],
            filter_branch=claims["branch"],
            updated_at=datetime.now(),
            deactive=active_status.upper() == "DEACTIVE"
        )

        try:
            computer = computer_update.change_activate_computer(change_active_dto)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if computer is None:
            return {"msg": "Kesalahan pada ID, Cabang, atau sudah ada perubahan sebelumnya"}, 400

        return jsonify(computer), 200
