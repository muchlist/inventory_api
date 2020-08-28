from databases.db import mongo
from dto.user_dto import UserDto


def insert_user(data: UserDto):
    data_insert = {
        "username": data.username.upper(),
        "password": data.password,
        "email": data.email,
        "name": data.name.upper(),
        "isAdmin": data.is_admin,
        "isEndUser": data.is_end_user,
        "branch": data.branch.upper(),
    }

    mongo.db.users.insert_one(data_insert)


def put_password(username: str, new_password: str):
    query = {"username": username}
    update = {'$set': {"password": new_password}}

    mongo.db.users.update_one(query, update)


def update_user(data: UserDto):
    find = {"username": data.username}
    update = {
        "name": data.name.upper(),
        "email": data.email,
        "isAdmin": data.is_admin,
        "isEndUser": data.is_end_user,
        "branch": data.branch.upper(),
    }

    mongo.db.users.update_one(find, {'$set': update})


def delete_user(username: str):
    mongo.db.users.remove({"username": username})
