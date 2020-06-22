from marshmallow import Schema, fields

class HistoryInsertSchema(Schema):
    category = fields.Str(required=True)
    status = fields.Str(required=True)
    note = fields.Str(required=True)
    date = fields.DateTime(required=False)