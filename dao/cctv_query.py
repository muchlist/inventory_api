from bson.objectid import ObjectId

from databases.db import mongo


def get_cctv(cctv_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(cctv_id),
    }
    return mongo.db.cctv.find_one(find_filter)


def get_cctv_with_branch(cctv_id: str, branch: str) -> dict:
    find_filter = {
        '_id': ObjectId(cctv_id),
        'branch': branch.upper()
    }
    return mongo.db.cctv.find_one(find_filter)


def find_cctv_by_branch_ip_cctv_name(branch: str,
                                     location: str,
                                     last_ping: str,
                                     ip_address: str,
                                     cctv_name: str,
                                     deactive: str) -> list:
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
    if last_ping:
        find_filter["last_ping"] = last_ping.upper()
    if location:
        find_filter["location"] = location
    if cctv_name:
        find_filter["cctv_name"] = {'$regex': f'.*{cctv_name.upper()}.*'}

    projection = {"_id": 1,
                  "branch": 1,
                  "cctv_name": 1,
                  "ip_address": 1,
                  "last_ping": 1,
                  "last_status": 1,
                  "location": 1,
                  "ping_state": 1,
                  "case": 1,
                  "case_size": 1,
                  }

    cctv_coll = mongo.db.cctv.find(find_filter, projection).sort(
        [("case_size", -1), ("last_ping", 1), ("location", -1)])
    cctvs = []

    for cctv in cctv_coll:

        # Inject sum ping state
        sum_ping = 0
        ping_list = cctv["ping_state"]
        for ping in ping_list:
            sum_ping += ping["code"]
        del cctv["ping_state"]
        cctv["ping_sum"] = int(sum_ping / len(ping_list) * 50)

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


def find_cctv_must_check(branch: str) -> list:
    find_filter = {
        "deactive": False,
        "last_ping": "DOWN",
        "case_size": int(0)
    }
    if branch:
        find_filter["branch"] = branch.upper()

    projection = {"_id": 1,
                  "branch": 1,
                  "cctv_name": 1,
                  "ip_address": 1,
                  "last_ping": 1,
                  "last_status": 1,
                  "location": 1,
                  "ping_state": 1,
                  "case": 1,
                  "case_size": 1,
                  }

    cctv_coll = mongo.db.cctv.find(find_filter, projection).sort("cctv_name", 1)

    cctv_list = []

    for cctv in cctv_coll:

        # Inject sum ping state
        sum_ping = 0
        ping_list = cctv["ping_state"]
        for ping in ping_list:
            sum_ping += ping["code"]
        del cctv["ping_state"]
        cctv["ping_sum"] = int(sum_ping / len(ping_list) * 50)
        if cctv["ping_sum"] == 0:
            cctv_list.append(cctv)

    return cctv_list
