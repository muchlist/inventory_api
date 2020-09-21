from bson.objectid import ObjectId

from databases.db import mongo


def get_apps_history(history_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(history_id),
    }
    return mongo.db.apps_histories.find_one(find_filter)


def find_apps_history_for_parent_app(parent_id: str) -> list:
    find_filter = {"parent_id": str(parent_id)}
    projection = {"_id": 1,
                  "parent_name": 1,
                  "title": 1,
                  "author": 1,
                  "branch": 1,
                  "desc": 1,
                  "resolve_note": 1,
                  "duration_minute": 1,
                  "status": 1,
                  "start_date": 1,
                  "is_complete": 1,
                  }
    histories_coll = mongo.db.apps_histories.find(find_filter, projection).sort("_id", -1)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories


def find_histories_by_name_branch_category(app_name: str, branch: str, category: str, limit: int) -> list:
    find_filter = {}
    if app_name:
        find_filter["parent_name"] = app_name.upper()
    if branch:
        find_filter["branch"] = branch.upper()
    if category:
        find_filter["category"] = category.upper()
    if not limit:
        limit = 100

    projection = {
        "_id": 1,
        "parent_name": 1,
        "title": 1,
        "branch": 1,
        "author": 1,
        "desc": 1,
        "resolve_note": 1,
        "duration_minute": 1,
        "status": 1,
        "start_date": 1,
        "is_complete": 1,
    }

    histories_coll = mongo.db.apps_histories.find(
        find_filter, projection).sort("_id", -1).limit(limit)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories
