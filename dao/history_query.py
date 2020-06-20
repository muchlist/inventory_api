from databases.db import mongo


def find_query_for_parent(parent_id: str) -> list:

    find = {"parent_id": parent_id}
    histories = []
    histories_coll = mongo.db.histories.find(find).sort({"updated_at": -1})
    for history in histories_coll:
        histories.append(history)
    return histories
