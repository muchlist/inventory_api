from databases.db import mongo
from dto.computer_dto import ComputerDto, SpecDto


def create_computer(data: ComputerDto) -> dict:

    spec_embed = {
        "processor": data.spec.processor,
        "ram": data.spec.ram,
        "hardisk": data.spec.hardisk,
        "score": data.spec.score,
    }
    data_insert = {
        "created_at": data.created_at,
        "updated_at": data.updated_at,
        "client_name": data.client_name.upper(),
        "hostname": data.hostname,
        "ip_address": data.ip_address,
        "inventory_number": data.inventory_number,
        "author": data.author,
        "branch": data.branch.upper(),
        "location": data.location,
        "division": data.division,
        "seat_management": data.seat_management,
        "year": data.year,
        "merk": data.merk,
        "tipe": data.tipe,
        "operation_system": data.operation_system,
        "last_status": data.last_status,
        "note": data.note,
        "spec": spec_embed
    }

    mongo.db.computer.insert_one(data_insert)

    return data_insert


