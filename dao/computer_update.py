from datetime import datetime

from bson.objectid import ObjectId

from databases.db import mongo
from dto.computer_dto import ComputerDto, ComputerEditDto, ComputerChangeActiveDto


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
        "deactive": data.deactive,
        "case": [],
        "spec": spec_embed
    }

    mongo.db.computer.insert_one(data_insert)

    return data_insert


def update_computer(data: ComputerEditDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "client_name": data.client_name.upper(),
        "hostname": data.hostname,
        "ip_address": data.ip_address,
        "inventory_number": data.inventory_number,
        "author": data.author,
        "location": data.location,
        "division": data.division,
        "seat_management": data.seat_management,
        "year": data.year,
        "merk": data.merk,
        "tipe": data.tipe,
        "operation_system": data.operation_system,
        "note": data.note,
        "deactive": data.deactive,
        "spec.processor": data.spec.processor,
        "spec.ram": data.spec.ram,
        "spec.hardisk": data.spec.hardisk,
        "spec.score": data.spec.score,
    }

    computer = mongo.db.computer.find_one_and_update(find, {'$set': update}, return_document=True)
    return computer


def delete_computer(computer_id: str, branch: str, time_limit: datetime) -> dict:
    find = {
        "_id": ObjectId(computer_id),
        "branch": branch,
        "created_at": {'$gte': time_limit},
    }

    computer = mongo.db.computer.find_one_and_delete(find)
    return computer


def update_last_status_computer(computer_id: str, branch: str, last_status: str) -> dict:
    find = {
        "_id": ObjectId(computer_id),
        "branch": branch.upper(),
    }
    update = {
        "last_status": last_status,
    }

    computer = mongo.db.computer.find_one_and_update(find, {'$set': update}, return_document=True)
    return computer


def insert_case_computer(computer_id: str, branch: str, case_id: str, case: str) -> dict:
    find = {
        "_id": ObjectId(computer_id),
        "branch": branch.upper(),
    }
    update = {
        '$push': {"case": {"case_id": case_id, "case_note": case}},
    }

    computer = mongo.db.computer.find_one_and_update(find, update, return_document=True)
    return computer


def delete_case_computer(computer_id: str, branch: str, case_id: str) -> dict:
    find = {
        "_id": ObjectId(computer_id),
        "branch": branch.upper(),
    }
    update = {
        '$pull': {"case": {"case_id": case_id}},
    }

    computer = mongo.db.computer.find_one_and_update(find, update, return_document=True)
    return computer


def change_activate_computer(data: ComputerChangeActiveDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "deactive": data.deactive,
    }

    computer = mongo.db.computer.find_one_and_update(find, {'$set': update}, return_document=True)
    return computer
