from marshmallow import Schema, fields, validate

class FolderSchema(Schema):
    """Schema for folder data validation"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    type = fields.Str(validate=validate.OneOf(["private", "team"]), default="private")
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    created_by = fields.Int(dump_only=True)

class FolderUpdateSchema(Schema):
    """Schema for folder update validation"""
    name = fields.Str(validate=validate.Length(min=1, max=255))
    type = fields.Str(validate=validate.OneOf(["private", "team"])) 