from datetime import datetime

from bson.objectid import ObjectId

from databases.db import mongo
from dto.cctv_dto import CctvDto, PingState, CctvEditDto


def create_cctv(data: CctvDto) -> dict:

    ping_state_dict = {
        "time_second": 0,
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
