from bson.objectid import ObjectId

from databases.db import mongo


def get_stock(stock_id: str) -> dict:
    find_filter = {
        '_id': ObjectId(stock_id),
    }
    return mongo.db.stock.find_one(find_filter)


def find_stock_by_branch(branch: str, stock_name: str, deactive: str) -> list:
    find_filter = {}
    if branch:
        find_filter["branch"] = branch.upper()
    if deactive:
        if deactive == "yes":
            find_filter["deactive"] = True
        elif deactive == "no":
            find_filter["deactive"] = False
    if stock_name:
        find_filter["cctv_name"] = {'$regex': f'.*{stock_name.upper()}.*'}

    stock_coll = mongo.db.stock.find(find_filter).sort(
        [("category", 1), ("stock_name", 1)])
    stocks = []
    for stock in stock_coll:
        stocks.append(stock)

    return stocks
