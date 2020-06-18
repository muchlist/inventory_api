from marshmallow import Schema, fields

class UserRegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Email(required=True)
    name = fields.Str(required=True)
    isAdmin = fields.Bool(required=True)
    isEndUser = fields.Bool(required=True)
    branch = fields.Str(required=True)


class UserEditSchema(Schema):
    password = fields.Str(required=True)
    email = fields.Email(required=True)
    name = fields.Str(required=True)
    isAdmin = fields.Bool(required=True)
    isEndUser = fields.Bool(required=True)
    branch = fields.Str(required=True)


class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class UserChangePassSchema(Schema):
    password = fields.Str(required=True)
    new_password = fields.Str(required=True)