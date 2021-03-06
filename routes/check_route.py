from datetime import datetime, timedelta

from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (check_obj_query, check_obj_update, cctv_query, check_update, check_query)
from dto.check_dto import CheckDto, CheckObjEmbedDto, EditCheckDto, CheckObjEmbedEditDto
from dto.check_obj_dto import EditCheckObjBySystemDto
from input_schemas.check import CheckInsertSchema, CheckEditSchema, CheckEmbedChildSchema
from validations.role_validation import is_end_user

bp = Blueprint('checklist_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
List check object localhost:5001/check-obj?branch=&name=?
------------------------------------------------------------------------------
"""


@bp.route("/check", methods=['GET', 'POST'])
@jwt_required
def find_check():
    claims = get_jwt_claims()

    if request.method == 'POST':
        schema = CheckInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        shift = data["shift"]

        obj_embed_list = []
        check_obj_list = check_obj_query.find_check_obj(
            branch=claims["branch"],
            name="",
            obj_type="",
            problem=0  # select all, 1 just have problem
        )
        for obj in check_obj_list:
            # jika obj memiliki shift yang sama dengan shift request
            # atau obj memiliki problem. maka masukkan ke dalam daftar check
            shift_match = shift in obj["shifts"]
            if obj["have_problem"] or shift_match:
                obj_embed = CheckObjEmbedDto(
                    id=str(obj["_id"]),
                    name=obj["name"],
                    is_checked=False,
                    checked_at=None,
                    checked_note=obj["checked_note"],
                    have_problem=obj["have_problem"],
                    complete_status=obj["complete_status"],
                    location=obj["location"],
                    type=obj["type"],
                    image_path="",
                    tag_one=obj["tag_one"],
                    tag_two=obj["tag_two"],
                    tag_one_selected="",
                    tag_two_selected="",
                )._asdict()
                obj_embed_list.append(obj_embed)

        check_obj_cctv = cctv_query.find_cctv_must_check(claims["branch"])
        for cctv in check_obj_cctv:
            obj_cctv = CheckObjEmbedDto(
                id=str(cctv["_id"]),
                name=cctv["cctv_name"],
                is_checked=False,
                checked_at=None,
                checked_note="",
                have_problem=True,
                complete_status=0,
                location=cctv["location"],
                type="CCTV",
                image_path="",
                tag_one=[],
                tag_two=[],
                tag_one_selected="",
                tag_two_selected="",
            )._asdict()
            obj_embed_list.append(obj_cctv)

        check_dto = CheckDto(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=claims["name"],
            branch=claims["branch"],
            is_finish=False,
            shift=shift,
            checks_obj=obj_embed_list
        )

        try:
            result = check_update.create_check(check_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':
        check = check_query.find_check(branch=claims["branch"], )

        return {"check": check}, 200


"""
------------------------------------------------------------------------------
Detail check obj localhost:5001/check/objectID
------------------------------------------------------------------------------
"""


@bp.route("/check/<chk_id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def detail_check(chk_id):
    if not ObjectId.is_valid(chk_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'GET':

        try:
            check = check_query.get_check(chk_id)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if check is None:
            return {"msg": "Check ID tidak ditemukan"}, 404

        return jsonify(check), 200

    if request.method == 'PUT':
        schema = CheckEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        check_edit_dto = EditCheckDto(
            filter_id=chk_id,
            filter_branch=claims["branch"],
            filter_author=claims["name"],

            branch=claims["branch"],
            updated_at=datetime.now(),
            shift=data["shift"],
            is_finish=data["is_finish"],
        )

        try:
            result = check_update.update_check(check_edit_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        if result is None:
            return {"msg": "Gagal mengedit data, cek kesamaan id, user dan cabang!"}, 400

        return jsonify(result), 200

    if request.method == 'DELETE':

        # dua puluh empat jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=24)

        try:
            check = check_update.delete_check(
                chk_id, claims["branch"], time_limit)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if check is None:
            return {"msg": "Gagal menghapus checklist, batas waktu 24 jam telah tercapai !"}, 400

        return {"msg": "check berhasil di hapus"}, 204


"""
------------------------------------------------------------------------------
check-finish localhost:5001/check-finish/objectID
------------------------------------------------------------------------------
"""


@bp.route("/check-finish/<chk_id>", methods=['GET'])
@jwt_required
def finish_check(chk_id):
    if not ObjectId.is_valid(chk_id):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'GET':

        data = EditCheckDto(
            branch=claims["branch"],
            filter_id=chk_id,
            filter_branch=claims["branch"],
            filter_author=claims["name"],
            is_finish=True,
            updated_at=datetime.now(),
            shift=0
        )

        try:
            check = check_update.finish_check(data)
        except:
            return {"msg": "Gagal mengambil data dari database"}, 500

        if check is None:
            return {"msg": "Check gagal diselesesaikan"}, 404

        return jsonify(check), 200


"""
------------------------------------------------------------------------------
Update check child localhost:5001/update-check/<check_id>/<child_id>
------------------------------------------------------------------------------
"""


@bp.route("/update-check/<check_id>/<child_id>", methods=['PUT'])
@jwt_required
def update_child_check(check_id, child_id):
    if not (ObjectId.is_valid(check_id) and ObjectId.is_valid(child_id)):
        return {"msg": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'PUT':
        schema = CheckEmbedChildSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return {"msg": str(err.messages)}, 400

        if not is_end_user(claims):
            return {"msg": "User tidak memiliki hak akses"}, 400

        is_checked = data["is_checked"]  # bool
        checked_note = data["checked_note"]  # str
        have_problem = data["have_problem"]  # bool
        complete_status = data["complete_status"]  # int
        tag_one_selected = data["tag_one_selected"]  # str
        tag_two_selected = data["tag_two_selected"]  # str

        child_dto = CheckObjEmbedEditDto(
            filter_parent_id=check_id,
            filter_id=child_id,
            filter_author=claims["name"],
            checked_at=datetime.now(),
            is_checked=is_checked,
            have_problem=have_problem,
            complete_status=complete_status,
            checked_note=checked_note,
            tag_one_selected=tag_one_selected,
            tag_two_selected=tag_two_selected,
        )

        try:
            result = check_update.update_child_check_data(child_dto)
        except:
            return {"msg": "Gagal menyimpan data ke database"}, 500

        if result is None:
            return {"msg": "gagal merubah data, cek kesesuaian id, cabang dan user"}, 400
        else:
            # check is child id existing in database check obj
            # if type is cctv it is not exist
            if check_type_of_child_is_not_cctv(child_id, result["checks_obj"]):
                check_obj_update.update_check_obj_by_system(
                    EditCheckObjBySystemDto(
                        filter_id=child_id,
                        updated_at=datetime.now(),
                        checked_note=checked_note,
                        have_problem=have_problem,
                        complete_status=complete_status
                    )
                )
            else:  # is cctv
                pass  # todo cctv must be crazy

        return jsonify(result), 201


def check_type_of_child_is_not_cctv(child_id: str, data: list):
    for x in data:
        if x["id"] == child_id:
            if x["type"] == "CCTV":
                return False
    return True
