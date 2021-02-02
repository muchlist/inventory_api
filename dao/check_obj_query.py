from bson.objectid import ObjectId

from databases.db import mongo

_ID = "_id"
_CREATED_AT = "created_at"
_UPDATED_AT = "updated_at"
_NAME = "name"
_BRANCH = "branch"
_LOCATION = "location"
_TYPE = "type"
_NOTE = "note"

_CHECKED_NOTE = "checked_note"
_HAVE_PROBLEM = "have_problem"
_IS_RESOLVE = "is_resolve"


def get_check_obj(check_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(check_id),
    }
    return mongo.db.check_obj.find_one(find_filter)


def find_check_obj(branch: str,
                   name: str,
                   obj_type: str,
                   problem: int, ) -> list:
    find_filter = {}
    if branch:
        find_filter[_BRANCH] = branch.upper()
    if name and name != "":
        find_filter[_NAME] = {'$regex': f'.*{name.upper()}.*'}
    if obj_type and obj_type != "":
        find_filter[_TYPE] = obj_type.upper()
    if problem == 1:
        find_filter[_HAVE_PROBLEM] = problem

    check_coll = mongo.db.check_obj.find(find_filter).sort([(_TYPE, -1), (_NAME, 1)])
    checks = []
    for check in check_coll:
        checks.append(check)

    return checks
