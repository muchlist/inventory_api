from bson.objectid import ObjectId

from databases.db import mongo


def get_apps(apps_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(apps_id),
    }
    return mongo.db.apps.find_one(find_filter)


def find_apps_and_filter(apps_name: str, branch: str) -> list:
    find_filter = {}
    if apps_name:
        find_filter["apps_name"] = {'$regex': f'.*{apps_name.upper()}.*'}
    if branch:
        find_filter["branches"] = branch.upper()

    projection = {
        "_id": 1,
        "apps_name": 1,
    }

    apps_coll = mongo.db.apps.find(find_filter, projection).sort(
        [("apps_name", 1)])
    apps = []

    for app in apps_coll:
        apps.append(app)

    return apps
