from marshmallow import Schema, fields

class HistoryInsertSchema(Schema):
    parent_id = fields.Str(required=True)
    category = fields.Str(required=True)
    status = fields.Str(required=True)
    note = fields.Str(required=True)
    date = fields.Date(required=False)