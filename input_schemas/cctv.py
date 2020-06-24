from marshmallow import Schema, fields


class CctvInsertSchema(Schema):
    cctv_name = fields.Str(required=True)
    ip_address = fields.Str(required=True)
    inventory_number = fields.Str(required=True)
    location = fields.Str(required=True)
    year = fields.DateTime(required=True)
    merk = fields.Str(required=True)
    tipe = fields.Str(required=True)
    note = fields.Str(required=True)
    deactive = fields.Bool(required=True)


class CctvEditSchema(Schema):
    cctv_name = fields.Str(required=True)
    ip_address = fields.Str(required=True)
    inventory_number = fields.Str(required=True)
    location = fields.Str(required=True)
    year = fields.DateTime(required=True)
    merk = fields.Str(required=True)
    note = fields.Str(required=True)
    deactive = fields.Bool(required=True)
    tipe = fields.Str(required=True)

    timestamp = fields.DateTime(required=True)
