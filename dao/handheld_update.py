from datetime import datetime

from bson.objectid import ObjectId

from databases.db import mongo
from dto.handheld_dto import HandheldDto, HandheldEditDto, HandheldChangeActiveDto


def create_handheld(data: HandheldDto) -> dict:
    data_insert = {
        "created_at": data.created_at,
        "updated_at": data.updated_at,
        "handheld_name": data.handheld_name.upper(),
        "ip_address": data.ip_address,
        "inventory_number": data.inventory_number,
        "author": data.author,
        "branch": data.branch.upper(),
        "location": data.location,
        "year": data.year,
        "merk": data.merk,
        "tipe": data.tipe,
        "note": data.note,
        "phone": data.phone,
        "last_status": data.last_status,
        "deactive": data.deactive,
        "case": [],
        "case_size": int(0),
    }

    mongo.db.handheld.insert_one(data_insert)

    return data_insert


def update_handheld(data: HandheldEditDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "handheld_name": data.handheld_name.upper(),
        "ip_address": data.ip_address,
        "inventory_number": data.inventory_number,
        "author": data.author,
        "location": data.location,
        "year": data.year,
        "merk": data.merk,
        "tipe": data.tipe,
        "note": data.note,
        "phone": data.phone,
        "deactive": data.deactive,
    }

    handheld = mongo.db.handheld.find_one_and_update(find, {'$set': update}, return_document=True)
    return handheld


def delete_handheld(hh_id: str, branch: str, time_limit: datetime) -> dict:
    find = {
        "_id": ObjectId(hh_id),
        "branch": branch,
        "created_at": {'$gte': time_limit},
    }

    hh = mongo.db.handheld.find_one_and_delete(find)
    return hh


def update_last_status_handheld(hh_id: str, branch: str, last_status: str) -> dict:
    find = {
        "_id": ObjectId(hh_id),
        "branch": branch.upper(),
    }
    update = {
        "last_status": last_status,
    }

    hh = mongo.db.handheld.find_one_and_update(find, {'$set': update}, return_document=True)
    return hh


def insert_case_handheld(handheld_id: str, branch: str, case_id: str, case: str) -> dict:
    find = {
        "_id": ObjectId(handheld_id),
        "branch": branch.upper(),
    }
    update = {
        '$push': {"case": {"case_id": case_id, "case_note": case}},
        '$inc': {"case_size": 1},
    }

    handheld = mongo.db.handheld.find_one_and_update(find, update, return_document=True)
    return handheld


def delete_case_handheld(handheld_id: str, branch: str, case_id: str) -> dict:
    find = {
        "_id": ObjectId(handheld_id),
        "branch": branch.upper(),
    }
    update = {
        '$pull': {"case": {"case_id": case_id}},
        '$inc': {"case_size": -1},
    }

    handheld = mongo.db.handheld.find_one_and_update(find, update, return_document=True)
    return handheld


def change_activate_handheld(data: HandheldChangeActiveDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "deactive": data.deactive,
    }

    hh = mongo.db.handheld.find_one_and_update(find, {'$set': update}, return_document=True)
    return hh
