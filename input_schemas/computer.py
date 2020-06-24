from marshmallow import Schema, fields


class ComputerInsertSchema(Schema):
    client_name = fields.Str(required=True)
    hostname = fields.Str(required=True)
    ip_address = fields.Str(required=True)
    inventory_number = fields.Str(required=True)
    location = fields.Str(required=True)
    division = fields.Str(required=True)
    seat_management = fields.Bool(required=True)
    year = fields.DateTime(required=True)
    merk = fields.Str(required=True)
    tipe = fields.Str(required=True)
    operation_system = fields.Str(required=True)
    note = fields.Str(required=True)
    processor = fields.Int(required=True)
    ram = fields.Int(required=True)
    hardisk = fields.Int(required=True)
    deactive = fields.Bool(required=True)


class ComputerEditSchema(Schema):
    client_name = fields.Str(required=True)
    hostname = fields.Str(required=True)
    ip_address = fields.Str(required=True)
    inventory_number = fields.Str(required=True)
    location = fields.Str(required=True)
    division = fields.Str(required=True)
    seat_management = fields.Bool(required=True)
    year = fields.DateTime(required=True)
    merk = fields.Str(required=True)
    operation_system = fields.Str(required=True)
    note = fields.Str(required=True)
    processor = fields.Int(required=True)
    ram = fields.Int(required=True)
    hardisk = fields.Int(required=True)
    deactive = fields.Bool(required=True)

    timestamp = fields.DateTime(required=True)
