from marshmallow import Schema, fields


class CheckInsertSchema(Schema):
    shift = fields.Int(required=True)


class CheckEditSchema(Schema):
    shift = fields.Int(required=True)
    is_finish = fields.Bool(required=True)
