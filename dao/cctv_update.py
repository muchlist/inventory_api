from datetime import datetime

from bson.objectid import ObjectId

from databases.db import mongo
from dto.cctv_dto import CctvDto, CctvEditDto, CctvChangeActiveDto


def create_cctv(data: CctvDto) -> dict:
    ping_state_dict = {
        "code": 0,
        "time_date": datetime.now(),
        "status": "DOWN",
    }

    data_insert = {
        "created_at": data.created_at,
        "updated_at": data.updated_at,
        "cctv_name": data.cctv_name.upper(),
        "ip_address": data.ip_address,
        "inventory_number": data.inventory_number,
        "author": data.author,
        "branch": data.branch.upper(),
        "location": data.location,
        "year": data.year,
        "merk": data.merk,
        "tipe": data.tipe,
        "last_status": data.last_status,
        "note": data.note,
        "deactive": data.deactive,
        "ping_state": [ping_state_dict],
        "last_ping": "DOWN",
        "image": "",
        "case": [],
        "case_size": int(0),
    }

    mongo.db.cctv.insert_one(data_insert)

    return data_insert


def update_cctv(data: CctvEditDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "cctv_name": data.cctv_name.upper(),
        "ip_address": data.ip_address,
        "inventory_number": data.inventory_number,
        "author": data.author,
        "location": data.location,
        "year": data.year,
        "merk": data.merk,
        "note": data.note,
        "deactive": data.deactive,
    }

    cctv = mongo.db.cctv.find_one_and_update(find, {'$set': update}, return_document=True)
    return cctv


def update_cctv_image(filter_id: str, image_path: str) -> dict:
    find = {
        "_id": ObjectId(filter_id)
    }
    update = {
        "updated_at": datetime.now(),
        "image": image_path
    }

    cctv = mongo.db.cctv.find_one_and_update(find, {'$set': update}, return_document=True)
    return cctv


def delete_cctv(cctv_id: str, branch: str, time_limit: datetime) -> dict:
    find = {
        "_id": ObjectId(cctv_id),
        "branch": branch,
        "created_at": {'$gte': time_limit},
    }

    cctv = mongo.db.cctv.find_one_and_delete(find)
    return cctv


def update_last_status_cctv(cctv_id: str, branch: str, last_status: str) -> dict:
    find = {
        "_id": ObjectId(cctv_id),
        "branch": branch.upper(),
    }
    update = {
        "last_status": last_status,
    }

    cctv = mongo.db.cctv.find_one_and_update(find, {'$set': update}, return_document=True)
    return cctv


def insert_case_cctv(cctv_id: str, branch: str, case_id: str, case: str) -> dict:
    find = {
        "_id": ObjectId(cctv_id),
        "branch": branch.upper(),
    }
    update = {
        '$push': {"case": {"case_id": case_id, "case_note": case}},
        '$inc': {"case_size": 1},
    }

    cctv = mongo.db.cctv.find_one_and_update(find, update, return_document=True)
    return cctv


def delete_case_cctv(cctv_id: str, branch: str, case_id: str) -> dict:
    find = {
        "_id": ObjectId(cctv_id),
        "branch": branch.upper(),
    }
    update = {
        '$pull': {"case": {"case_id": case_id}},
        '$inc': {"case_size": -1},
    }

    cctv = mongo.db.cctv.find_one_and_update(find, update, return_document=True)
    return cctv


def change_activate_cctv(data: CctvChangeActiveDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "deactive": data.deactive,
    }

    cctv = mongo.db.cctv.find_one_and_update(find, {'$set': update}, return_document=True)
    return cctv


def append_status_ping_cctv(ip_address_list: list, ping_code: int) -> int:
    # 2 up , 1 half, 0 down
    ping_code_dict = {
        0: "DOWN",
        1: "HALF",
        2: "UP"
    }

    ping_state_dict = {
        "code": ping_code,
        "time_date": datetime.now(),
        "status": ping_code_dict.get(ping_code),
    }

    filter_cctv = {
        "ip_address": {'$in': ip_address_list}
    }

    update = {
        '$push': {"ping_state": {'$each': [ping_state_dict, ], '$position': 0, '$slice': 12}},
        '$set': {"last_ping": ping_state_dict.get("status")}
    }

    try:
        mongo.db.cctv.update(filter_cctv, update, multi=True)
    except:
        return 400

    return 200
