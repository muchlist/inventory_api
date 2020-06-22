from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    get_jwt_claims,
)
from input_schemas.computer import (ComputerInsertSchema)
from dao import (computer_query,
                 computer_update)
from dto.computer_dto import ComputerDto, SpecDto

from datetime import datetime

bp = Blueprint('computer_bp', __name__, url_prefix='/api')


"""
------------------------------------------------------------------------------
List komputer dan Membuat Komputer
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
            return err.messages, 400

        data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        data["branch"] = claims["branch"]
        data["author"] = claims["name"]
        data["last_status"] = "INIT"

        data["score"] = 0

        spec_dto = SpecDto(
            processor=data["processor"],
            ram=data["ram"],
            hardisk=data["hardisk"],
            score=data["score"],
        )

        computer_dto = ComputerDto(
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            client_name=data["client_name"],
            hostname=data["hostname"],
            ip_address=data["ip_address"],
            inventory_number=data["inventory_number"],
            author=data["author"],
            branch=data["branch"],
            location=data["location"],
            division=data["division"],
            seat_management=data["seat_management"],
            year=data["year"],
            merk=data["merk"],
            tipe=data["tipe"],
            operation_system=data["operation_system"],
            last_status=data["last_status"],
            note=data["note"],
            spec=spec_dto,
        )

        try:
            result = computer_update.create_computer(computer_dto)
        except:
            return {"message": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':

        ip_address = request.args.get("ip_address")
        client_name = request.args.get("client_name")

        computers = computer_query.find_computer_by_branch_ip_clientname(
            claims["branch"], ip_address, client_name)

        return {"computers": computers}, 200
