from databases.db import mongo


def find_history_for_parent(parent_id: str) -> list:
    filter = {"parent_id": parent_id}
    histories_coll = mongo.db.histories.find(filter).sort("date", -1)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories


def find_histories_by_branch_by_category(branch: str, category: str) -> list:
    filter = {}
    if branch:
        filter["branch"] = branch.upper()
    if category:
        filter["category"] = category.upper()

    histories_coll = mongo.db.histories.find(
        filter).sort("date", -1).limit(100)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories
