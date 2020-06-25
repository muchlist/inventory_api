from datetime import datetime, timedelta

from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
)
from marshmallow import ValidationError

from dao import (stock_update,
                 stock_query,
                 )
from dto.stock_dto import StockDto, StockEditDto, UseStockDto
from input_schemas.stock import (StockInsertSchema, StockEditSchema, StockUseSchema)
from validations.role_validation import isEndUser

bp = Blueprint('stock_bp', __name__, url_prefix='/api')

"""
------------------------------------------------------------------------------
GET : List stock localhost:5001/stocks?branch=?&stock_name=?deactive=
POST : Membuat Stock
------------------------------------------------------------------------------
"""


@bp.route("/stocks", methods=['GET', 'POST'])
@jwt_required
def find_stock():
    claims = get_jwt_claims()

    if request.method == 'POST':

        schema = StockInsertSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if not isEndUser(claims):
            return {"message": "User tidak memiliki hak akses"}, 401

        stock_dto = StockDto(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            stock_name=data["stock_name"],
            author=claims["name"],
            branch=claims["branch"],
            location=data["location"],
            note=data["note"],
            category=data["category"],
            qty=float(data["qty"]),
            threshold=float(data["threshold"]),
            unit=data["unit"],
            increment=[],
            decrement=[],
            deactive=data["deactive"],
        )

        try:
            result = stock_update.create_stock(stock_dto)
        except:
            return {"message": "Gagal menyimpan data ke database"}, 500

        return jsonify(result), 201

    if request.method == 'GET':
        stock_name = request.args.get("stock_name")
        deactive = request.args.get("deactive")
        branch = claims["branch"]

        if request.args.get("branch"):
            branch = request.args.get("branch")

        stocks = stock_query.find_stock_by_branch(
            branch, stock_name, deactive)

        return {"stocks": stocks}, 200


"""
------------------------------------------------------------------------------
Detail stock localhost:5001/stocks/objectID
------------------------------------------------------------------------------
"""


@bp.route("/stocks/<stock_id>", methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def detail_stock(stock_id):
    if not ObjectId.is_valid(stock_id):
        return {"message": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()

    if request.method == 'GET':

        try:
            stock = stock_query.get_stock(stock_id)
        except:
            return {"message": "Gagal mengambil data dari database"}, 500

        if stock is None:
            return {"message": "Stock dengan ID tersebut tidak ditemukan"}, 404

        return jsonify(stock), 200

    if request.method == 'PUT':
        schema = StockEditSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if not isEndUser(claims):
            return {"message": "User tidak memiliki hak akses"}, 401

        stock_edit_dto = StockEditDto(
            filter_id=stock_id,
            filter_timestamp=data["timestamp"],
            filter_branch=claims["branch"],

            updated_at=datetime.now(),
            category=data["category"],
            threshold=float(data["threshold"]),
            unit=data["unit"],
            stock_name=data["stock_name"],
            author=claims["name"],
            location=data["location"],
            note=data["note"],
            deactive=data["deactive"],
        )

        try:
            result = stock_update.update_stock(stock_edit_dto)
        except:
            return {"message": "Gagal menyimpan data ke database"}, 500

        if result is None:
            return {"message": "gagal update stock, data telah diubah oleh orang lain sebelumnya"}, 400

        return jsonify(result), 200

    if request.method == 'DELETE':

        # dua jam kurang dari sekarang
        time_limit = datetime.now() - timedelta(hours=2)

        try:
            stock = stock_update.delete_stock(
                stock_id, claims["branch"], time_limit)
        except:
            return {"message": "Gagal mengambil data dari database"}, 500

        if stock is None:
            return {"message": "gagal menghapus stock, batas waktu hanya dua jam setelah pembuatan"}, 400

        return {"message": "stock berhasil di hapus"}, 204


"""
------------------------------------------------------------------------------
Detail stock localhost:5001/use-stock/objectID
------------------------------------------------------------------------------
"""


@bp.route("/use-stock/<stock_id>", methods=['POST'])
@jwt_required
def use_stock(stock_id):
    if not ObjectId.is_valid(stock_id):
        return {"message": "Object ID tidak valid"}, 400

    claims = get_jwt_claims()
    schema = StockUseSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return err.messages, 400

    if not isEndUser(claims):
        return {"message": "User tidak memiliki hak akses"}, 401

    mode_available = ["INCREMENT", "DECREMENT"]
    if data["mode"].upper() not in mode_available:
        return {"message": "Pilihan input pada mode harus INCREMENT atau DECREMENT"}, 400

    use_stock_dto = UseStockDto(
        parent_id=stock_id,
        author=claims["name"],
        ba_number=data["ba_number"],
        branch=claims["branch"],
        note=data["note"],
        time=data["time"],
        qty=data["qty"]
    )

    if data["mode"] == "INCREMENT":
        try:
            result = stock_update.increment(use_stock_dto)
        except:
            return {"message": "Gagal menyimpan data ke database"}, 500

    else:  # DECREMENT
        try:
            result = stock_update.decrement(use_stock_dto)
        except:
            return {"message": "Gagal menyimpan data ke database"}, 500

    if result is None:
        return {"message": "gagal update stock, jumlah stock tidak mencukupi"}, 400

    return jsonify(result), 200
