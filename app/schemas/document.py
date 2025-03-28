from marshmallow import Schema, fields, validate

class DocumentSchema(Schema):
    """Schema for document data validation"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str()
    file_url = fields.Str(dump_only=True)
    file_path = fields.Str(dump_only=True)
    file_type = fields.Str(dump_only=True)
    file_size = fields.Int(dump_only=True)
    tags = fields.List(fields.Str(), default=[])
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    created_by = fields.Int(dump_only=True)

class DocumentUpdateSchema(Schema):
    """Schema for document update validation"""
    title = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str()
    tags = fields.List(fields.Str()) 