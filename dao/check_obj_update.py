from bson.objectid import ObjectId

from databases.db import mongo
from dto.check_obj_dto import CheckObjDto, EditCheckObjDto

_ID = "_id"
_CREATED_AT = "created_at"
_UPDATED_AT = "updated_at"
_NAME = "name"
_BRANCH = "branch"
_LOCATION = "location"
_TYPE = "type"
_LAST_STATUS = "last_status"
_NOTE = "note"


def create_check_obj(data: CheckObjDto) -> dict:
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

    mongo.db.check_obj.insert_one(data_insert)

    return data_insert


def update_check_obj(data: EditCheckObjDto) -> dict:
    find = {
        _ID: ObjectId(data.filter_id),
        _BRANCH: data.filter_branch,
    }
    update = {
        _UPDATED_AT: data.updated_at,
        _NAME: data.name.upper(),
        _BRANCH: data.branch.upper(),
        _LOCATION: data.location,
        _TYPE: data.type.upper(),
        _NOTE: data.note,
    }

    check_obj = mongo.db.check_obj.find_one_and_update(find, {'$set': update}, return_document=True)
    return check_obj


def delete_check_obj(check_id: str, branch: str) -> dict:
    find = {
        _ID: ObjectId(check_id),
        _BRANCH: branch,
    }

    check_obj = mongo.db.check_obj.find_one_and_delete(find)
    return check_obj
