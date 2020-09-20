from marshmallow import Schema, fields


class HandheldInsertSchema(Schema):
    handheld_name = fields.Str(required=True)
    ip_address = fields.Str(required=True)
    inventory_number = fields.Str(required=True)
    location = fields.Str(required=True)
    year = fields.DateTime(required=True)
    merk = fields.Str(required=True)
    tipe = fields.Str(required=True)
    phone = fields.Str(required=True)
    note = fields.Str(required=True)
    deactive = fields.Bool(required=True)


class HandheldEditSchema(Schema):
    handheld_name = fields.Str(required=True)
    ip_address = fields.Str(required=True)
    inventory_number = fields.Str(required=True)
    location = fields.Str(required=True)
    year = fields.DateTime(required=True)
    merk = fields.Str(required=True)
    tipe = fields.Str(required=True)
    phone = fields.Str(required=True)
    note = fields.Str(required=True)
    deactive = fields.Bool(required=True)

    timestamp = fields.DateTime(required=True)


class HandheldChangeActiveSchema(Schema):
    timestamp = fields.DateTime(required=True)
