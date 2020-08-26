from marshmallow import Schema, fields


class StockInsertSchema(Schema):
    stock_name = fields.Str(required=True)
    location = fields.Str(required=True)
    category = fields.Str(required=True)
    qty = fields.Float(required=True)
    unit = fields.Str(required=True)
    threshold = fields.Float(required=True)
    note = fields.Str(required=True)
    deactive = fields.Bool(required=True)


class StockEditSchema(Schema):
    stock_name = fields.Str(required=True)
    location = fields.Str(required=True)
    category = fields.Str(required=True)
    unit = fields.Str(required=True)
    threshold = fields.Float(required=True)
    note = fields.Str(required=True)
    deactive = fields.Bool(required=True)

    timestamp = fields.DateTime(required=True)


class StockUseSchema(Schema):
    mode = fields.Str(required=True)
    qty = fields.Float(required=True)
    ba_number = fields.Str(required=True)
    note = fields.Str(required=True)
    time = fields.DateTime(required=True)


class StockChangeActiveSchema(Schema):
    timestamp = fields.DateTime(required=True)
