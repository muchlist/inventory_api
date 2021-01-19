from datetime import datetime

from bson.objectid import ObjectId

from databases.db import mongo
from dto.check_dto import CheckDto, EditCheckDto, CheckObjEmbedInsertPhotoDto, CheckObjEmbedEditDto

_ID = "_id"
_CREATED_AT = "created_at"
_CREATED_BY = "created_by"
_UPDATED_AT = "updated_at"
_SHIFT = "shift"
_BRANCH = "branch"
_IS_FINISH = "is_finish"
_CHECKS_OBJ = "checks_obj"
_CHECKS_CCTV = "checks_cctv"

_CHECKS_OBJ__ID = "checks_obj.id"
_CHECKS_OBJ__IMAGE_PATH = "checks_obj.$.image_path"
_CHECKS_OBJ__CHECKED_AT = "checks_obj.$.checked_at"
_CHECKS_OBJ__IS_CHECKED = "checks_obj.$.is_checked"
_CHECKS_OBJ__CHECKED_NOTE = "checks_obj.$.checked_note"
_CHECKS_OBJ__IS_RESOLVE = "checks_obj.$.is_resolve"


def create_check(data: CheckDto) -> dict:
    data_insert = {
        _CREATED_AT: data.created_at,
        _CREATED_BY: data.created_at,
        _UPDATED_AT: data.updated_at,
        _SHIFT: data.shift,
        _BRANCH: data.branch.upper(),
        _IS_FINISH: data.is_finish,
        _CHECKS_OBJ: data.checks_obj,
    }

    mongo.db.check.insert_one(data_insert)

    return data_insert


def update_check(data: EditCheckDto) -> dict:
    find = {
        _ID: ObjectId(data.filter_id),
        _BRANCH: data.filter_branch,
    }
    update = {
        _UPDATED_AT: data.updated_at,
        _SHIFT: data.shift,
        _BRANCH: data.branch.upper(),
        _IS_FINISH: data.is_finish,
    }

    check = mongo.db.check.find_one_and_update(find, {'$set': update}, return_document=True)
    return check


def delete_check(check_id: str, branch: str) -> dict:
    find = {
        _ID: ObjectId(check_id),
        _BRANCH: branch,
    }

    check_obj = mongo.db.check.find_one_and_delete(find)
    return check_obj


def update_child_check_image(data: CheckObjEmbedInsertPhotoDto) -> dict:
    find = {
        _ID: ObjectId(data.filter_parent_id),
        _CHECKS_OBJ__ID: data.filter_id
    }

    update = {
        _UPDATED_AT: datetime.now(),
        _CHECKS_OBJ__IMAGE_PATH: data.image_path
    }

    check = mongo.db.check.find_one_and_update(find, {'$set': update}, return_document=True)
    return check


def update_child_check_data(data: CheckObjEmbedEditDto) -> dict:
    find = {
        _ID: ObjectId(data.filter_parent_id),
        _CHECKS_OBJ__ID: data.filter_id
    }

    update = {
        _UPDATED_AT: datetime.now(),
        _CHECKS_OBJ__IS_CHECKED: data.is_checked,
        _CHECKS_OBJ__CHECKED_AT: data.checked_at,
        _CHECKS_OBJ__CHECKED_NOTE: data.checked_note,
        _CHECKS_OBJ__IS_RESOLVE: data.is_resolve
    }

    check = mongo.db.check.find_one_and_update(find, {'$set': update}, return_document=True)
    return check
