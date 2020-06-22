from databases.db import mongo
from dto.history_dto import HistoryDto


def insert_history(data: HistoryDto):
    data_insert = {
        "parent_id": data.parent_id,
        "parent_name": data.parent_name,
        "category": data.category.upper(),
        "author": data.author.upper(),
        "branch": data.branch.upper(),
        "status": data.status.upper(),
        "note": data.note,
        "date": data.date,
    }

    mongo.db.histories.insert_one(data_insert)
