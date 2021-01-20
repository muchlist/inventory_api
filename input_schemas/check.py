from marshmallow import Schema, fields


class CheckInsertSchema(Schema):
    shift = fields.Int(required=True)


class CheckEditSchema(Schema):
    shift = fields.Int(required=True)
    is_finish = fields.Bool(required=True)


# input edit child dalam sebuah check
class CheckEmbedChildSchema(Schema):
    is_checked = fields.Bool(required=True)
    checked_note = fields.Str(required=True)
    is_resolve = fields.Bool(required=True)
    have_problem = fields.Bool(required=True)
