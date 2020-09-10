from datetime import datetime

from bson import ObjectId

from databases.db import mongo
from dto.apps_histo_dto import AppsHistoDto, AppsEditHistoDto


def insert_apps_history(data: AppsHistoDto) -> str:
    data_insert = {
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "title": data.title.upper(),
        "desc": data.desc.lower(),
        "parent_id": str(data.parent_id),
        "parent_name": data.parent_name,
        "status": data.status.upper(),
        "author": data.author.upper(),
        "author_id": data.author_id.upper(),
        "branch": data.branch.upper(),
        "location": data.location,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "is_complete": data.is_complete,
        "duration_minute": data.duration,
        "resolve_note": data.resolve_note,
        "pic": data.pic
    }

    return mongo.db.apps_histories.insert_one(data_insert).inserted_id


def update_apps_histo(data: AppsEditHistoDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
        "is_complete": False,
    }
    update = {
        "updated_at": datetime.now(),
        "title": data.title.upper(),
        "desc": data.desc.lower(),
        "status": data.status.upper(),  # Api down , jaringan, unknown
        "author": data.author.upper(),
        "author_id": data.author_id.upper(),
        "location": data.location,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "is_complete": data.is_complete,
        "duration_minute": data.duration,
        "resolve_note": data.resolve_note,
        "pic": data.pic
    }

    apps_histories = mongo.db.apps_histories.find_one_and_update(find, {'$set': update}, return_document=True)

    return apps_histories


def delete_apps_history(history_id: str, branch: str, time_limit: datetime) -> dict:
    find_filter = {
        "_id": ObjectId(history_id),
        "branch": branch.upper(),
        "created_at": {'$gte': time_limit},
    }

    return mongo.db.apps_histories.find_one_and_delete(find_filter)
