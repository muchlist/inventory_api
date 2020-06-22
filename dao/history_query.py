from databases.db import mongo


def find_history_for_parent(parent_id: str) -> list:

    filter = {"parent_id": parent_id}
    histories_coll = mongo.db.histories.find(filter).sort("updated_at", -1)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories


def find_histories_by_branch_by_category(branch: str, category: str) -> list:

    filter = {}
    if branch:
        find["branch"] = branch.upper()
    if category:
        find["category"] = category.upper()

    histories_coll = mongo.db.histories.find(
        filter).sort("updated_at", -1).limit(100)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories
