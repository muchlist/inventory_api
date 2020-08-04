from bson.objectid import ObjectId

from databases.db import mongo


def get_cctv(cctv_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(cctv_id),
    }
    return mongo.db.cctv.find_one(find_filter)


def find_cctv_by_branch_ip_cctv_name(branch: str, ip_address: str, cctv_name: str, deactive: str) -> list:
    find_filter = {}
    if branch:
        find_filter["branch"] = branch.upper()
    if deactive:
        if deactive == "yes":
            find_filter["deactive"] = True
        elif deactive == "no":
            find_filter["deactive"] = False
    if ip_address:
        find_filter["ip_address"] = ip_address
    if cctv_name:
        find_filter["cctv_name"] = {'$regex': f'.*{cctv_name.upper()}.*'}

    projection = {"_id": 1,
                  "branch": 1,
                  "cctv_name": 1,
                  "ip_address": 1,
                  "last_ping": 1,
                  "last_status": 1,
                  "location": 1,
                  }

    cctv_coll = mongo.db.cctv.find(find_filter, projection).sort(
        [("last_ping", 1), ("cctv_name", 1)])
    cctvs = []
    for cctv in cctv_coll:
        cctvs.append(cctv)

    return cctvs


def find_cctv_ip_list(branch: str, location: str) -> list:
    find_filter = {}
    if branch:
        find_filter["branch"] = branch.upper()
    if location:
        find_filter["location"] = location.upper()

    projection = {"ip_address": 1}

    cctv_coll = mongo.db.cctv.find(find_filter, projection)
    cctv_ip_address_list = []
    for cctv in cctv_coll:
        cctv_ip_address_list.append(cctv["ip_address"])

    return cctv_ip_address_list
