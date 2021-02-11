from marshmallow import Schema, fields


class HistoryInsertSchema(Schema):
    category = fields.Str(required=True)
    status = fields.Str(required=True)
    note = fields.Str(required=True)
    location = fields.Str(required=True)
    date = fields.DateTime(required=False)
    end_date = fields.DateTime(required=False, allow_none=True)
    resolve_note = fields.Str(required=True)
    # is_complete = fields.Bool(required=True)
    complete_status = fields.Int(required=True)


class HistoryEditSchema(Schema):
    category = fields.Str(required=True)
    status = fields.Str(required=True)
    note = fields.Str(required=True)
    location = fields.Str(required=True)
    date = fields.DateTime(required=False)
    end_date = fields.DateTime(required=True)
    resolve_note = fields.Str(required=True)
    # is_complete = fields.Bool(required=True)
    complete_status = fields.Int(required=True)

    timestamp = fields.DateTime(required=True)
