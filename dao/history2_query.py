from bson.objectid import ObjectId

from databases.db import mongo


def get_history(history_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(history_id),
    }
    return mongo.db.histories.find_one(find_filter)


def find_history_for_parent(parent_id: str) -> list:
    find_filter = {"parent_id": str(parent_id)}
    projection = {"_id": 1,
                  "parent_name": 1,
                  "category": 1,
                  "author": 1,
                  "branch": 1,
                  "note": 1,
                  "resolve_note": 1,
                  "duration_minute": 1,
                  "status": 1,
                  "start_date": 1,
                  "is_complete": 1,
                  "timestamp": 1,
                  }

    histories_coll = mongo.db.histories.find(find_filter, projection).sort("_id", -1)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories


def find_history_for_user(author_id: str, limit: int) -> list:
    find_filter = {"author_id": author_id}
    if not limit:
        limit = 100

    histories_coll = mongo.db.histories.find(find_filter).sort("_id", -1).limit(limit)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories


def find_histories_by_branch_by_category(branch: str, category: str, is_complete: int, limit: int) -> list:
    find_filter = {}
    if branch:
        find_filter["branch"] = branch.upper()
    if category:
        find_filter["category"] = category.upper()

    if is_complete == 0:
        find_filter["is_complete"] = False
    elif is_complete == 1:
        find_filter["is_complete"] = True

    if not limit:
        limit = 100

    histories_coll = mongo.db.histories.find(
        find_filter).sort("_id", -1).limit(limit)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories
