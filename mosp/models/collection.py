import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

from mosp.bootstrap import db


class Collection(db.Model):
    """Represent a collection."""

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), default="")
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow)

    # foreign keys
    creator_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return self.name
