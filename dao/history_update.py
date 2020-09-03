from datetime import datetime

from bson import ObjectId

from databases.db import mongo
from dto.history_dto import HistoryDto


def insert_history(data: HistoryDto) -> str:
    data_insert = {
        "parent_id": str(data.parent_id),
        "parent_name": data.parent_name,
        "category": data.category.upper(),
        "author": data.author.upper(),
        "author_id": data.author_id.upper(),
        "branch": data.branch.upper(),
        "status": data.status.upper(),
        "note": data.note,
        "date": data.date,
        "timestamp": datetime.now(),
    }

    return mongo.db.histories.insert_one(data_insert).inserted_id


def delete_history(history_id: str, branch: str, time_limit: datetime) -> dict:
    find_filter = {
        "_id": ObjectId(history_id),
        "branch": branch.upper(),
        "timestamp": {'$gte': time_limit},
    }

    return mongo.db.histories.find_one_and_delete(find_filter)
