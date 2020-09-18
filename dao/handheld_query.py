from bson.objectid import ObjectId

from databases.db import mongo


def get_handheld(hh_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(hh_id),
    }
    return mongo.db.handheld.find_one(find_filter)


def get_handheld_with_branch(hh_id: str, branch: str) -> dict:
    find_filter = {
        '_id': ObjectId(hh_id),
        'branch': branch.upper()
    }
    return mongo.db.handheld.find_one(find_filter)


def find_handheld_by_branch_handheld_name(branch: str,
                                          location: str,
                                          hh_name: str,
                                          deactive: str) -> list:
    find_filter = {}
    if branch:
        find_filter["branch"] = branch.upper()
    if deactive:
        if deactive == "yes":
            find_filter["deactive"] = True
        elif deactive == "no":
            find_filter["deactive"] = False
    if location:
        find_filter["location"] = location
    if hh_name:
        find_filter["handheld_name"] = {'$regex': f'.*{hh_name.upper()}.*'}

    projection = {"_id": 1,
                  "branch": 1,
                  "handheld_name": 1,
                  "ip_address": 1,
                  "last_status": 1,
                  "location": 1,
                  }

    hh_coll = mongo.db.handheld.find(find_filter, projection).sort("location", -1)
    hhs = []

    for hh in hh_coll:
        hhs.append(hh)

    return hhs
