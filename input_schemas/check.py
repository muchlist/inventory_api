from marshmallow import Schema, fields


class CheckInsertSchema(Schema):
    shift = fields.Int(required=True)