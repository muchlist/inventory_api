from marshmallow import Schema, fields


class AppsHistoryInsertSchema(Schema):
    title = fields.Str(required=True)
    desc = fields.Str(required=True)
    location = fields.Str(required=True)
    status = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=False, allow_none=True)
    resolve_note = fields.Str(required=True)
    pic = fields.Str(required=True)
    is_complete = fields.Bool(required=True)


class AppsHistoryEditSchema(Schema):
    title = fields.Str(required=True)
    desc = fields.Str(required=True)
    location = fields.Str(required=True)
    status = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True, allow_none=True)
    resolve_note = fields.Str(required=True)
    pic = fields.Str(required=True)
    is_complete = fields.Bool(required=True)

    timestamp = fields.DateTime(required=True)
