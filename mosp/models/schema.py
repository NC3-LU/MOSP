from datetime import datetime

from sqlalchemy import event
from sqlalchemy.dialects.postgresql import JSONB

from mosp.bootstrap import db

association_table_license = db.Table(
    "association_schemas_licenses",
    db.metadata,
    db.Column("schema_id", db.Integer, db.ForeignKey("schema.id")),
    db.Column("license_id", db.Integer, db.ForeignKey("license.id")),
)


class Schema(db.Model):
    """Represent a JSON schema."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow)
    json_schema = db.Column(JSONB, default={})

    # relationship
    objects = db.relationship(
        "JsonObject", backref="schema", lazy="dynamic", cascade="all,delete-orphan"
    )
    licenses = db.relationship(
        "License", secondary=lambda: association_table_license, backref="schemas"
    )

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey("organization.id"), default=None)
    creator_id = db.Column(db.Integer(), db.ForeignKey("user.id"), default=True)


@event.listens_for(Schema, "before_update")
def update_modified_on_update_listener(mapper, connection, target):
    """Event listener that runs before a record is updated, and sets the
    last_updated field accordingly.
    """
    target.last_updated = datetime.utcnow()
