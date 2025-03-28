from datetime import datetime
from app import db

class Document(db.Model):
    """Document model for file storage and management"""
    
    __tablename__ = "documents"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = db.relationship("User", back_populates="documents")
    tags = db.relationship("DocumentTag", back_populates="document", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Return a dict representation of the document"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "fileUrl": self.file_url,
            "fileType": self.file_type,
            "fileSize": self.file_size,
            "tags": [tag.name for tag in self.tags],
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "createdBy": self.created_by
        }
    
    def __repr__(self):
        return f"<Document {self.title}>"


class DocumentTag(db.Model):
    """Document tag model"""
    
    __tablename__ = "document_tags"
    
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), primary_key=True)
    name = db.Column(db.String(50), primary_key=True)
    
    # Relationships
    document = db.relationship("Document", back_populates="tags")
    
    def __repr__(self):
        return f"<DocumentTag {self.name}>" 