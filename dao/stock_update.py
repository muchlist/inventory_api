import time
from datetime import datetime

from bson.objectid import ObjectId

from databases.db import mongo
from dto.stock_dto import StockDto, StockEditDto, UseStockDto, StockChangeActiveDto


def create_stock(data: StockDto) -> dict:
    data_increment_init = {
        "dummy_id": int(time.time()),
        "author": data.author,
        "qty": data.qty,
        "ba_number": "INIT",
        "note": "INIT",
        "time": data.created_at,
    }

    data_insert = {
        "created_at": data.created_at,
        "updated_at": data.updated_at,
        "stock_name": data.stock_name.upper(),
        "category": data.category,
        "unit": data.unit,
        "qty": data.qty,
        "threshold": data.threshold,
        "author": data.author,
        "branch": data.branch.upper(),
        "location": data.location,
        "note": data.note,
        "deactive": data.deactive,
        "increment": [data_increment_init, ],
        "decrement": [],
        "image": ""
    }

    mongo.db.stock.insert_one(data_insert)

    return data_insert


def update_stock(data: StockEditDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "stock_name": data.stock_name.upper(),
        "author": data.author,
        "location": data.location,
        "threshold": data.threshold,
        "category": data.category,
        "unit": data.unit,
        "note": data.note,
        "deactive": data.deactive,
    }

    stock = mongo.db.stock.find_one_and_update(find, {'$set': update}, return_document=True)
    return stock


def increment(data: UseStockDto) -> dict:
    increment_embed = {
        "dummy_id": int(time.time()),
        "author": data.author,
        "qty": data.qty,
        "ba_number": data.ba_number,
        "note": data.note,
        "time": data.time
    }

    find = {
        "_id": ObjectId(data.parent_id),
        "branch": data.branch,
    }

    update = {
        '$set': {"updated_at": datetime.now()},
        '$inc': {"qty": data.qty},
        '$push': {"increment": increment_embed}
    }

    stock = mongo.db.stock.find_one_and_update(find, update, return_document=True)
    return stock


def decrement(data: UseStockDto) -> dict:
    decrement_embed = {
        "dummy_id": int(time.time()),
        "author": data.author,
        "qty": data.qty,
        "ba_number": data.ba_number,
        "note": data.note,
        "time": data.time
    }

    find = {
        "_id": ObjectId(data.parent_id),
        "branch": data.branch,
        "qty": {'$gte': data.qty},
    }

    minus_data_qty = -data.qty

    update = {
        '$set': {"updated_at": datetime.now()},
        '$inc': {"qty": minus_data_qty},
        '$push': {"decrement": decrement_embed}
    }

    stock = mongo.db.stock.find_one_and_update(find, update, return_document=True)
    return stock


def delete_stock(stock_id: str, branch: str, time_limit: datetime) -> dict:
    find = {
        "_id": ObjectId(stock_id),
        "branch": branch,
        "created_at": {'$gte': time_limit},
    }

    stock = mongo.db.stock.find_one_and_delete(find)
    return stock


def change_activate_stock(data: StockChangeActiveDto) -> dict:
    find = {
        "_id": ObjectId(data.filter_id),
        "branch": data.filter_branch,
        "updated_at": data.filter_timestamp,
    }
    update = {
        "updated_at": data.updated_at,
        "deactive": data.deactive,
    }

    stock = mongo.db.stock.find_one_and_update(find, {'$set': update}, return_document=True)
    return stock


def update_stock_image(filter_id: str, image_path: str) -> dict:
    find = {
        "_id": ObjectId(filter_id)
    }
    update = {
        "updated_at": datetime.now(),
        "image": image_path
    }

    stock = mongo.db.stock.find_one_and_update(find, {'$set': update}, return_document=True)
    return stock

