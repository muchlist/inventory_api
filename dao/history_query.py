from databases.db import mongo


def find_history_for_parent(parent_id: str) -> list:
    find_filter = {"parent_id": str(parent_id)}
    histories_coll = mongo.db.histories.find(find_filter).sort("_id", -1)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories


def find_history_for_user(author_id: str, limit: int) -> list:
    find_filter = {"author_id": author_id}
    if not limit:
        limit = 100

    histories_coll = mongo.db.histories.find(find_filter).sort("_id", -1).limit(limit)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories


def find_histories_by_branch_by_category(branch: str, category: str, limit: int) -> list:
    find_filter = {}
    if branch:
        find_filter["branch"] = branch.upper()
    if category:
        find_filter["category"] = category.upper()
    if not limit:
        limit = 100

    histories_coll = mongo.db.histories.find(
        find_filter).sort("_id", -1).limit(limit)
    histories = []
    for history in histories_coll:
        histories.append(history)

    return histories
