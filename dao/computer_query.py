from databases.db import mongo
from bson.objectid import ObjectId


def get_computer(id: str) -> dict:
    filter = {
        '_id': ObjectId(id),
    }
    return mongo.db.computer.find_one(filter)


def find_computer_by_branch_ip_clientname(branch: str, ip_address: str, client_name: str) -> list:

    filter = {}
    if branch:
        filter["branch"] = branch
    if ip_address:
        filter["ip_address"] = ip_address
    if client_name:
        filter["client_name"] = {'$regex': f'.*{client_name.upper()}.*'}

    computer_coll = mongo.db.computer.find(filter).sort(
        [("division", 1), ("client_name", 1)])
    computers = []
    for computer in computer_coll:
        computers.append(computer)

    return computers
