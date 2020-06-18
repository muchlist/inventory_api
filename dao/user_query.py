from databases.db import mongo


def get_one(username: str) -> dict:
    user = mongo.db.users.find_one({"username": username})
    return user


def get_one_without_password(username: str) -> dict:
    result = mongo.db.users.find_one(
        {"username": username}, {"password": 0})
    return result


def get_many_by_name(name: str) -> list:
    query_string = {'$regex': f'.*{name.upper()}.*'}

    user_collection = mongo.db.users.find(
        {"name": query_string}, {"password": 0})

    user_list = []

    for user in user_collection:
        user_list.append(user)

    return user_list


def get_many() -> list:
    user_list = []
    result = mongo.db.users.find({}, {"password": 0})
    for user in result:
        user_list.append(user)

    return user_list


def get_all_company() -> list:
    all_company_array = mongo.db.users.distinct('company')
    return all_company_array
