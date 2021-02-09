from bson.objectid import ObjectId

from databases.db import mongo
from bson.son import SON


def get_history(history_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(history_id),
    }
    return mongo.db.histories.find_one(find_filter)


def find_history_for_parent(parent_id: str) -> list:
    find_filter = {"parent_id": str(parent_id)}
    histories_coll = mongo.db.histories.find(find_filter).sort("_id", -1)
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


def find_histories_by_branch_by_category(branch: str, category: str, complete_status: int, limit: int) -> list:
    find_filter = {}
    if branch:
        find_filter["branch"] = branch.upper()
    if category:
        find_filter["category"] = category.upper()

    if complete_status:
        find_filter["complete_status"] = complete_status

    if not limit:
        limit = 100

    histories_coll = mongo.db.histories.find(
        find_filter).sort("timestamp", -1).limit(limit)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories


def get_histories_in_progress_count(branch: str) -> list:
    find_filter = {
        "complete_status": 0
    }
    if branch:
        find_filter["branch"] = branch.upper()

    pipeline = [
        {"$match": find_filter},
        {"$group": {"_id": "$branch", "count": {"$sum": 1}}},
        {"$sort": SON([("count", -1), ("_id", -1)])}
    ]

    # history_on_progress = mongo.db.histories.find(find_filter).count()
    cursor = mongo.db.histories.aggregate(pipeline)

    results = []
    for res in cursor:
        results.append(res)

    return results
