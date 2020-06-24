from flask import Blueprint, request
from flask_jwt_extended import (

    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (user_query,
                 user_update)
from dto.user_dto import UserDto
from input_schemas.user import (UserRegisterSchema,

                                UserEditSchema)
from utils.my_bcrypt import bcrypt
from validations import role_validation as valid

bp = Blueprint('user_admin_bp', __name__, url_prefix='/admin')


def user_eksis(username):
    if user_query.get_one_without_password(username):
        return True
    return False


"""
------------------------------------------------------------------------------
register
------------------------------------------------------------------------------
"""


@bp.route('/register', methods=['POST'])
# @jwt_required
def register_user():
    # if not valid.isAdmin(get_jwt_claims()):
    #     return {"message": "user tidak memiliki authorisasi"}, 403

    schema = UserRegisterSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return err.messages, 400

    # hash password
    pw_hash = bcrypt.generate_password_hash(
        data["password"]).decode("utf-8")
    data["password"] = pw_hash

    # mengecek apakah user exist
    if user_eksis(data["username"]):
        return {"message": "user tidak tersedia"}, 400

    # mendaftarkan ke mongodb
    user_dto = UserDto(data["username"],
                       pw_hash,
                       data["name"],
                       data["email"],
                       data["isAdmin"],
                       data["isEndUser"],
                       data["branch"])
    # try:
    #     user_update.insert_user(user_dto)
    # except:
    #     return {"message": "gagal menyimpan ke database"}, 500
    user_update.insert_user(user_dto)
    return {"message": "data berhasil disimpan"}, 201


"""
------------------------------------------------------------------------------
Merubah dan mendelete user
------------------------------------------------------------------------------
"""


@bp.route('/users/<string:username>', methods=['PUT', 'DELETE'])
@jwt_required
def put_delete_user(username):
    if not valid.isAdmin(get_jwt_claims()):
        return {"message": "user tidak memiliki authorisasi"}, 403

    if request.method == 'PUT':
        schema = UserEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if not user_eksis(username):
            return {"message": f"user {username} tidak ditemukan"}, 404

        user_dto = UserDto(username, "", data["email"], data["isAdmin"], data["isEndUser"], data["branch"])

        try:
            user_update.update_user(user_dto)
        except:
            return {"message": "gagal menyimpan ke database"}, 500

        return {"message": f"user {username} berhasil diubah"}, 201

    if request.method == 'DELETE':
        if not user_eksis(username):
            return {"message": f"user {username} tidak ditemukan"}

        user_update.delete_user(username)
        return {"message": f"user {username} berhasil dihapus"}, 201


"""
------------------------------------------------------------------------------
Reset Password
------------------------------------------------------------------------------
"""


@bp.route('/reset/<string:username>', methods=['GET'])
@jwt_required
def reset_password_by_admin(username):
    if not valid.isAdmin(get_jwt_claims()):
        return {"message": "user tidak memiliki authorisasi"}, 403

    if request.method == 'GET':
        if not user_eksis(username):
            return {"message": f"user {username} tidak ditemukan"}, 404

        # hash password
        pw_hash = bcrypt.generate_password_hash("Pelindo3").decode("utf-8")

        user_update.put_password(username, pw_hash)

        return {"message": f"Password user {username} berhasil direset"}, 201
