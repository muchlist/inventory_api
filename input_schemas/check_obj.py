from marshmallow import Schema, fields


class CheckObjInsertSchema(Schema):
    name = fields.Str(required=True)
    location = fields.Str(required=True)
    type = fields.Str(required=True)
    shifts = fields.List(fields.Int, required=True)
    note = fields.Str(required=True)


class CheckObjEditSchema(Schema):
    name = fields.Str(required=True)
    location = fields.Str(required=True)
    type = fields.Str(required=True)
    shifts = fields.List(fields.Int, required=True)
    note = fields.Str(required=True)
