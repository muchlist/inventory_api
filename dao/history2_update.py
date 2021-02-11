from datetime import datetime

from bson import ObjectId

from databases.db import mongo
from dto.history2_dto import HistoryDto2, EditHistoryDto2


def insert_history(history_id: ObjectId, data: HistoryDto2) -> str:
    data_insert = {
        "_id": history_id,
        "parent_id": str(data.parent_id),
        "parent_name": data.parent_name,  # as title
        "category": data.category.upper(),
        "author": data.author.upper(),  # incident opened by
        "author_id": data.author_id.upper(),
        "branch": data.branch.upper(),
        "status": data.status.upper(),
        "note": data.note.lower(),  # as description
        "date": data.date,  # start_date
        "timestamp": datetime.now(),  # updated_at

        # extra
        "created_at": datetime.now(),
        "end_date": data.end_date,
        "location": data.location,
        # "is_complete": data.is_complete,
        "complete_status": data.complete_status,
        "duration_minute": data.duration,
        "resolve_note": data.resolve_note,
        "updated_by": data.updated_by,
        "updated_by_id": data.updated_by,
    }

    return mongo.db.histories.insert_one(data_insert).inserted_id


def update_history(data: EditHistoryDto2) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "timestamp": data.filter_timestamp,
        "complete_status": {"$ne": 2},  # 0 progress , 1 pending , 2 complete
    }
    update = {
        "status": data.status.upper(),
        "note": data.note.lower(),  # as description
        "date": data.date,  # start_date
        "end_date": data.end_date,
        "timestamp": datetime.now(),  # updated_at
        "location": data.location,
        # "is_complete": data.is_complete,
        "complete_status": data.complete_status,
        "duration_minute": data.duration,
        "resolve_note": data.resolve_note,
        "updated_by": data.updated_by,
        "updated_by_id": data.updated_by,
    }

    histories = mongo.db.histories.find_one_and_update(find, {'$set': update}, return_document=True)

    return histories


def delete_history(history_id: str, branch: str, time_limit: datetime) -> dict:
    find_filter = {
        "_id": ObjectId(history_id),
        "branch": branch.upper(),
        "created_at": {'$gte': time_limit},
    }

    return mongo.db.histories.find_one_and_delete(find_filter)
