from typing import Union
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref
from sqlalchemy import event

import jsonschema

from mosp.bootstrap import db
from mosp.models.version import Version
from mosp.models.schema import Schema


association_table_license = db.Table(
    "association_jsonobjects_licenses",
    db.metadata,
    db.Column("json_object_id", db.Integer, db.ForeignKey("json_object.id")),
    db.Column("license_id", db.Integer, db.ForeignKey("license.id")),
)

association_table_jsonobject = db.Table(
    "association_jsonobject_jsonobject",
    db.metadata,
    db.Column("jsonobject_refers_to_id", db.Integer, db.ForeignKey("json_object.id")),
    db.Column(
        "jsonobject_referred_to_by_id", db.Integer, db.ForeignKey("json_object.id")
    ),
)

association_table_collection = db.Table(
    "association_jsonobjects_collections",
    db.metadata,
    db.Column("json_object_id", db.Integer, db.ForeignKey("json_object.id")),
    db.Column("collection_id", db.Integer, db.ForeignKey("collection.id")),
)


class JsonObject(db.Model):
    """Represent a JSON object."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow)
    json_object = db.Column(JSONB, default={})
    is_locked = db.Column(db.Boolean(), default=False)

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey("organization.id"), nullable=False)
    schema_id = db.Column(db.Integer(), db.ForeignKey("schema.id"), nullable=False)
    creator_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    editor_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)

    # relationships
    collections = db.relationship(
        "Collection", secondary=lambda: association_table_collection, backref="objects"
    )

    licenses = db.relationship(
        "License", secondary=lambda: association_table_license, backref="objects"
    )

    refers_to = db.relationship(
        "JsonObject",
        secondary=lambda: association_table_jsonobject,
        primaryjoin=association_table_jsonobject.c.jsonobject_refers_to_id == id,
        secondaryjoin=association_table_jsonobject.c.jsonobject_referred_to_by_id == id,
        backref="referred_to_by",
    )

    versions = db.relationship(
        "Version", backref="head", lazy="dynamic", cascade="all,delete-orphan"
    )

    creator = db.relationship(
        "User",
        backref=backref("creator", uselist=False),
        uselist=False,
        foreign_keys=[creator_id],
    )

    editor = db.relationship(
        "User",
        backref=backref("editor", uselist=False),
        uselist=False,
        foreign_keys=[editor_id],
    )

    def __eq__(self, other):
        return self.id == other.id

    def create_new_version(self, obj: Union["JsonObject", None] = None) -> Version:
        """Create a new Version object from the JsonObject given in parameter or from
        the current object (self).
        Returns the new Version object."""
        if not obj:
            obj = self
        new_version = Version(
            name=obj.name,
            description=obj.description,
            last_updated=obj.last_updated,
            json_object=obj.json_object,
            object_id=obj.id,
            editor_id=obj.editor_id,
        )
        db.session.add(new_version)
        db.session.commit()
        return new_version

    def restore_from_version(self, version: Version):
        """Update the current JsonObject (self) with the specified Version object."""
        schema = Schema.query.filter(Schema.id == self.schema_id)
        try:
            # check that the Version to restore validates the current schema.
            jsonschema.validate(version.json_object, schema.first().json_schema)
        except jsonschema.exceptions.ValidationError:
            raise Exception(
                "The version to restore is not validated by the current schema."
            )

        self.name = version.name
        self.description = version.description
        self.json_object = version.json_object
        db.session.commit()
        return self


@event.listens_for(JsonObject, "before_update")
def update_modified_on_update_listener(mapper, connection, target):
    """Event listener that runs before a record is updated, and sets the
    last_updated field accordingly.
    """
    target.last_updated = datetime.utcnow()
