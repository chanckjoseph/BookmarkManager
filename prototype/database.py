from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Bookmark(db.Model):
    """The main bookmarks table."""
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False, index=True)
    title = db.Column(db.String)
    folder_path = db.Column(db.String, default="")
    source_browser = db.Column(db.String) # e.g. 'firefox', 'chrome'
    source_profile = db.Column(db.String) # Profile path
    
    # Version Control Metadata
    version = db.Column(db.Integer, default=1)
    status = db.Column(db.String, default='synced') # synced, conflict
    last_synced_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "folder": self.folder_path,
            "source": f"{self.source_browser} ({self.version})",
            "status": self.status,
            "tags": [t.to_dict() for t in self.tags]
        }

# Association Table for Many-to-Many
bookmark_tags = db.Table('bookmark_tags',
    db.Column('bookmark_id', db.Integer, db.ForeignKey('bookmarks.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Tag(db.Model):
    """Tags for categorizing bookmarks."""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

# Add relationship to Bookmark (Monkey-patching or defining here if circular)
# For simplicity, we define the backref on Tag, but since Bookmark is already defined above,
# we need to be careful. Ideally, relationship is defined on Bookmark or Tag.
# Let's add it to Tag, referring to 'Bookmark' by string to avoid order issues.
Tag.bookmarks = db.relationship('Bookmark', secondary=bookmark_tags, lazy='subquery',
        backref=db.backref('tags', lazy=True))

class SyncBatch(db.Model):
    """A transaction log for sync operations."""
    __tablename__ = 'sync_batches'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String) # e.g. 'firefox_auto'
    status = db.Column(db.String, default='pending_review') # pending_review, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to changes
    changes = db.relationship('PendingChange', backref='batch', lazy=True)

class PendingChange(db.Model):
    """Staging area for changes before they are committed."""
    __tablename__ = 'pending_changes'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('sync_batches.id'))
    
    # If updating an existing bookmark
    bookmark_id = db.Column(db.Integer, db.ForeignKey('bookmarks.id'), nullable=True)
    
    change_type = db.Column(db.String) # new, update, delete
    
    # Store the diff as JSON (e.g. {"title": {"old": "A", "new": "B"}})
    diff_blob = db.Column(db.String) 

    def get_diff(self):
        return json.loads(self.diff_blob) if self.diff_blob else {}
