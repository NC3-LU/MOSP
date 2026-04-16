import uuid
from datetime import datetime
from datetime import timezone

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
    date_created = db.Column(
        db.DateTime(), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    last_updated = db.Column(
        db.DateTime(), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # foreign keys
    creator_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return self.name
