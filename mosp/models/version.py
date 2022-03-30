from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from mosp.bootstrap import db


class Version(db.Model):
    """Represent a version of an object (only the fields 'name', 'description',
    'json_object' and 'last_updated' are versioned)."""

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow)
    json_object = db.Column(JSONB, default={})

    # relationships
    editor = db.relationship("User", backref="versions")

    # foreign keys
    object_id = db.Column(db.Integer(), db.ForeignKey("json_object.id"), nullable=False)
    editor_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
