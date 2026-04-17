import uuid

from sqlalchemy.dialects.postgresql import UUID

from mosp.bootstrap import db
from mosp.models._datetime import utcnow_naive


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
    date_created = db.Column(db.DateTime(), default=utcnow_naive)
    last_updated = db.Column(db.DateTime(), default=utcnow_naive)

    # foreign keys
    creator_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)

    def __str__(self):
        return self.name
