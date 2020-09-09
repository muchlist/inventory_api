from marshmallow import Schema, fields


class AppsInsertSchema(Schema):
    apps_name = fields.Str(required=True)
    description = fields.Str(required=True)
    url = fields.Str(required=True)
    platform = fields.Str(required=True)
    branches = fields.List(fields.String(), required=True)
    programmers = fields.List(fields.String(), required=True)
    note = fields.Str(required=True)


class AppsEditSchema(Schema):
    apps_name = fields.Str(required=True)
    description = fields.Str(required=True)
    url = fields.Str(required=True)
    platform = fields.Str(required=True)
    branches = fields.List(fields.String(), required=True)
    programmers = fields.List(fields.String(), required=True)
    note = fields.Str(required=True)

    timestamp = fields.DateTime(required=True)
