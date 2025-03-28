from datetime import datetime
from app import db

class Folder(db.Model):
    """Folder model for organizing documents"""
    
    __tablename__ = "folders"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False, default="private")  # 'private' or 'team'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = db.relationship("User", back_populates="folders")
    
    def to_dict(self):
        """Return a dict representation of the folder"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "createdBy": self.created_by
        }
    
    def __repr__(self):
        return f"<Folder {self.name}>"


class FolderDocument(db.Model):
    """Association table between folders and documents"""
    
    __tablename__ = "folder_documents"
    
    folder_id = db.Column(db.Integer, db.ForeignKey("folders.id"), primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), primary_key=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    folder = db.relationship("Folder", backref=db.backref("folder_documents", cascade="all, delete-orphan"))
    document = db.relationship("Document", backref=db.backref("folder_documents", cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f"<FolderDocument folder_id={self.folder_id} document_id={self.document_id}>"


class FolderPermission(db.Model):
    """Permissions for folder access"""
    
    __tablename__ = "folder_permissions"
    
    id = db.Column(db.Integer, primary_key=True)
    folder_id = db.Column(db.Integer, db.ForeignKey("folders.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    permission_type = db.Column(db.String(50), nullable=False, default="read")  # 'read', 'write', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    folder = db.relationship("Folder", backref=db.backref("permissions", cascade="all, delete-orphan"))
    user = db.relationship("User", backref=db.backref("folder_permissions", cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f"<FolderPermission folder_id={self.folder_id} user_id={self.user_id} type={self.permission_type}>" 