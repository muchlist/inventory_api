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

    cctv_coll = mongo.db.cctv.find(find_filter).sort(
        [("last_ping", 1), ("cctv_name", 1)])
    cctvs = []
    for cctv in cctv_coll:
        cctvs.append(cctv)

    return cctvs
