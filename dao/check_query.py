from bson.objectid import ObjectId

from databases.db import mongo

_ID = "_id"
_BRANCH = "branch"


def get_check(check_id: str) -> dict:
    find_filter = {
        _ID: ObjectId(check_id),
    }
    return mongo.db.check.find_one(find_filter)


def find_check(branch: str) -> list:
    find_filter = {}
    if branch:
        find_filter[_BRANCH] = branch.upper()

    projection = {
        "checks_obj": 0
    }

    check_coll = mongo.db.check.find(find_filter, projection).sort(_ID, -1).limit(40)
    checks = []
    for check in check_coll:
        checks.append(check)

    return checks
