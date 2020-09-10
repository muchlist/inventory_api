from datetime import datetime

from bson.objectid import ObjectId

from databases.db import mongo
from dto.apps_dto import AppsDto, AppsEditDto


def create_apps(data: AppsDto) -> dict:
    data_insert = {
        "created_at": data.created_at,
        "updated_at": data.updated_at,
        "apps_name": data.apps_name.upper(),
        "description": data.description,
        "programmers": [x.upper() for x in data.programmers],
        "branches": [x.upper() for x in data.branches],
        "note": data.note,
        "trouble_count": 0,
    }

    mongo.db.apps.insert_one(data_insert)

    return data_insert


def update_apps(data: AppsEditDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "apps_name": data.apps_name.upper(),
        "description": data.description,
        "programmers": [x.upper() for x in data.programmers],
        "branches": [x.upper() for x in data.branches],
        "note": data.note,
    }

    apps = mongo.db.apps.find_one_and_update(find, {'$set': update}, return_document=True)
    return apps


def reset_counter(apps_id: str, time_stamp: datetime) -> dict:
    find = {
        "_id": ObjectId(apps_id),
        "updated_at": time_stamp,
    }

    update = {
        '$set': {"updated_at": datetime.now(),
                 "trouble_count": 0, },
    }

    apps = mongo.db.apps.find_one_and_update(find, update, return_document=True)
    return apps


def increment_counter(filter_id: str, trouble: int) -> dict:
    find = {
        "_id": ObjectId(filter_id),
    }

    update = {
        '$inc': {"trouble_count": trouble},
    }

    apps = mongo.db.apps.find_one_and_update(find, update, return_document=True)
    return apps


def delete_apps(apps_id: str, time_limit: datetime) -> dict:
    find = {
        "_id": ObjectId(apps_id),
        "created_at": {'$gte': time_limit},
    }

    apps = mongo.db.apps.find_one_and_delete(find)
    return apps
