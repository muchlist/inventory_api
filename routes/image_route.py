import os
import time

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from flask_uploads import UploadNotAllowed
from marshmallow import ValidationError

from config import config as cf
from dao import cctv_query, cctv_update, stock_query, stock_update, check_query, check_update
from dto.check_dto import CheckObjEmbedInsertPhotoDto
from input_schemas.image import ImageSchema
from utils import image_helper
from validations.role_validation import is_end_user

# Set up a Blueprint
bp = Blueprint('container_image_bp', __name__, url_prefix='/api')


@bp.route('/cctvs/<cctv_id>/upload', methods=['POST'])
@jwt_required
def upload_cctv_image(cctv_id):
    # static/images/namafolder/namafile

    # Input Validation
    schema = ImageSchema()
    try:
        data = schema.load(request.files)
    except ValidationError as err:
        return err.messages, 400

    if not ObjectId.is_valid(cctv_id):
        return {"msg": "Object ID tidak valid"}, 400

    # AUTH
    claims = get_jwt_claims()
    if not is_end_user(claims):
        return {"msg": "User tidak memiliki hak akses"}, 400

    # Cek apakah cctv valid
    cctv_object = cctv_query.get_cctv_with_branch(cctv_id, claims["branch"])
    if cctv_object is None:
        return {"msg": "User tidak memiliki hak akses"}, 400
    exist_image = cctv_object["image"]

    # Mendapatkan extensi pada file yang diupload
    extension = image_helper.get_extension(data['image'])

    # Memberikan Nama file dan ekstensi
    file_name = f"{cctv_object['_id']}-{int(time.time())}{extension}"
    folder = "cctv"

    # Menghapus Image existing
    delete_image_existing(exist_image)

    # SAVE IMAGE
    try:
        image_path = image_helper.save_image(
            data['image'], folder=folder, name=file_name)
        # basename = image_helper.get_basename(image_path)  # mengembalikan image.jpg
    except UploadNotAllowed:
        extension = image_helper.get_extension(data['image'])
        return {"msg": f"extensi {extension} not allowed"}, 400

    cctv_updated = cctv_update.update_cctv_image(cctv_object['_id'], image_path)
    if cctv_updated is None:
        return {"msg": "Gagal menyimpan ke database"}, 400

    return jsonify(cctv_updated), 200


@bp.route('/stocks/<stock_id>/upload', methods=['POST'])
@jwt_required
def upload_stock_image(stock_id):
    # static/images/namafolder/namafile

    # Input Validation
    schema = ImageSchema()
    try:
        data = schema.load(request.files)
    except ValidationError as err:
        return err.messages, 400

    if not ObjectId.is_valid(stock_id):
        return {"msg": "Object ID tidak valid"}, 400

    # AUTH
    claims = get_jwt_claims()
    if not is_end_user(claims):
        return {"msg": "User tidak memiliki hak akses"}, 400

    # Cek apakah stock valid
    stock_object = stock_query.get_stock_with_branch(stock_id, claims["branch"])
    if stock_object is None:
        return {"msg": "User tidak memiliki hak akses"}, 400
    exist_image = stock_object["image"]

    # Mendapatkan extensi pada file yang diupload
    extension = image_helper.get_extension(data['image'])

    # Memberikan Nama file dan ekstensi
    file_name = f"{stock_object['_id']}-{int(time.time())}{extension}"
    folder = "stock"

    # Menghapus Image existing
    delete_image_existing(exist_image)

    # SAVE IMAGE
    try:
        image_path = image_helper.save_image(
            data['image'], folder=folder, name=file_name)
        # basename = image_helper.get_basename(image_path)  # mengembalikan image.jpg
    except UploadNotAllowed:
        extension = image_helper.get_extension(data['image'])
        return {"msg": f"extensi {extension} not allowed"}, 400

    stock_updated = stock_update.update_stock_image(stock_object['_id'], image_path)
    if stock_updated is None:
        return {"msg": "Gagal menyimpan ke database"}, 400

    return jsonify(stock_updated), 200


@bp.route('/check/<parent_id>/<child_id>/upload', methods=['POST'])
@jwt_required
def upload_check_image(parent_id, child_id):
    # static/images/namafolder/namafile
    # Input Validation
    schema = ImageSchema()
    try:
        data = schema.load(request.files)
    except ValidationError as err:
        return err.messages, 400

    if not (ObjectId.is_valid(parent_id) and ObjectId.is_valid(child_id)):
        return {"msg": "Object ID tidak valid"}, 400

    # AUTH
    claims = get_jwt_claims()
    if not is_end_user(claims):
        return {"msg": "User tidak memiliki hak akses"}, 400

    # Cek apakah check valid
    check_doc = check_query.get_check(parent_id)
    if check_doc is None or check_doc["created_by"] != claims["name"]:
        return {"msg": "Tidak dapat melakukan upload, cek kesesuaian ID dan user"}, 400

    # Mendapatkan extensi pada file yang diupload
    extension = image_helper.get_extension(data['image'])

    # Memberikan Nama file dan ekstensi
    file_name = f"{parent_id}-{child_id}-{int(time.time())}{extension}"
    folder = "check"

    # SAVE IMAGE
    try:
        image_path = image_helper.save_image(
            data['image'], folder=folder, name=file_name)
        # basename = image_helper.get_basename(image_path)  # mengembalikan image.jpg
    except UploadNotAllowed:
        extension = image_helper.get_extension(data['image'])
        return {"msg": f"extensi {extension} not allowed"}, 400

    insert_foto_dto = CheckObjEmbedInsertPhotoDto(
        filter_author=claims["name"],
        filter_parent_id=parent_id,
        filter_id=child_id,
        image_path=image_path,
    )

    check = check_update.update_child_check_image(insert_foto_dto)
    if check is None:
        return {"msg": "Gagal menyimpan ke database"}, 400

    return jsonify(check), 200



def delete_image_existing(exist_image: str):
    # Menghapus Image existing
    if exist_image != "":
        try:
            filepath = os.path.join(cf.get('uploaded_image_dest'), exist_image)
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            return {"msg": "Menghapus image eksisting gagal"}, 500
