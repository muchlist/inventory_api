from bson.objectid import ObjectId

from databases.db import mongo


def get_computer(id: str) -> dict:
    find_filter = {
        '_id': ObjectId(id),
    }
    return mongo.db.computer.find_one(find_filter)


def find_computer_by_branch_ip_clientname(branch: str,
                                          ip_address: str,
                                          client_name: str,
                                          location: str,
                                          division: str,
                                          seat: str,
                                          deactive: str) -> list:
    find_filter = {}
    if branch:
        find_filter["branch"] = branch.upper()
    if location:
        find_filter["location"] = location.upper()
    if division:
        find_filter["division"] = division.upper()
    if deactive:
        if deactive == "yes":
            find_filter["deactive"] = True
        elif deactive == "no":
            find_filter["deactive"] = False
    if seat:
        if seat == "yes":
            find_filter["seat_management"] = True
        elif seat == "no":
            find_filter["seat_management"] = False
    if ip_address:
        find_filter["ip_address"] = ip_address
    if client_name:
        find_filter["client_name"] = {'$regex': f'.*{client_name.upper()}.*'}

    visible_filter = {
        "_id": 1,
        "branch": 1,
        "client_name": 1,
        "location": 1,
        "division": 1,
        "seat_management": 1,
        "last_status": 1,
        "ip_address": 1,
        "case": 1,
        "case_size": 1,
    }

    computer_coll = mongo.db.computer.find(find_filter, visible_filter).sort(
        [("case_size", -1), ("location", 1), ("division", 1)])
    computers = []
    for computer in computer_coll:
        computers.append(computer)

    return computers
