from marshmallow import Schema, fields


class AppsHistoryInsertSchema(Schema):
    title = fields.Str(required=True)
    desc = fields.Str(required=True)
    location = fields.Str(required=True)
    category = fields.Str(required=True)
    status = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)


class AppsHistoryEditSchema(Schema):
    title = fields.Str(required=True)
    desc = fields.Str(required=True)
    location = fields.Str(required=True)
    category = fields.Str(required=True)
    status = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)

    timestamp = fields.DateTime(required=True)
