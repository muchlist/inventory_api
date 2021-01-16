from bson.objectid import ObjectId

from databases.db import mongo
from dto.master_check_dto import MasterCheckDto, MasterEditCheckDto

_ID = "_id"
_CREATED_AT = "created_at"
_UPDATED_AT = "updated_at"
_NAME = "name"
_BRANCH = "branch"
_LOCATION = "location"
_TYPE = "type"
_LAST_STATUS = "last_status"
_NOTE = "note"


def create_master_check(data: MasterCheckDto) -> dict:
    data_insert = {
        _CREATED_AT: data.created_at,
        _UPDATED_AT: data.updated_at,
        _NAME: data.name.upper(),
        _BRANCH: data.branch.upper(),
        _LOCATION: data.location,
        _TYPE: data.type,
        _LAST_STATUS: data.last_status,
        _NOTE: data.note,
    }

    mongo.db.master_check.insert_one(data_insert)

    return data_insert


def update_master_check(data: MasterEditCheckDto) -> dict:
    find = {
        _ID: ObjectId(data.filter_id),
        _BRANCH: data.filter_branch,
    }
    update = {
        _UPDATED_AT: data.updated_at,
        _NAME: data.name.upper(),
        _BRANCH: data.branch.upper(),
        _LOCATION: data.location,
        _TYPE: data.type,
        _NOTE: data.note,
    }

    master_check = mongo.db.master_check.find_one_and_update(find, {'$set': update}, return_document=True)
    return master_check


def delete_master_check(check_id: str, branch: str) -> dict:
    find = {
        _ID: ObjectId(check_id),
        _BRANCH: branch,
    }

    master_check = mongo.db.master_check.find_one_and_delete(find)
    return master_check
