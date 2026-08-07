from marshmallow import fields,Schema,validate,ValidationError

class Register_Schema(Schema):
    username=fields.Str(required=True,validate=validate.Length(min=3))
    email=fields.Str(required=True)
    password=fields.Str(required=True,validate=validate.Length(min=8))


class Login_Schema(Schema):
    username=fields.Str(required=True,validate=validate.Length(min=3))
    password=fields.Str(required=True,validate=validate.Length(min=8))