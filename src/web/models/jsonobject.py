
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import event
from web.models import User

from bootstrap import db

association_table_license = db.Table('association_jsonobjects_licenses',
    db.metadata,
    db.Column('json_object_id', db.Integer, db.ForeignKey('json_object.id')),
    db.Column('license_id', db.Integer, db.ForeignKey('license.id'))
)

association_table_jsonobject = db.Table('association_jsonobject_jsonobject',
    db.metadata,
    db.Column('jsonobject_refers_to_id', db.Integer, db.ForeignKey('json_object.id')),
    db.Column('jsonobject_referred_to_by_id', db.Integer, db.ForeignKey('json_object.id'))
)

class JsonObject(db.Model):
    """Represent a JSON object.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    is_public = db.Column(db.Boolean(), default=True)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow())
    json_object = db.Column(JSONB, default={})

    # relationship
    licenses = db.relationship("License",
                            secondary=lambda: association_table_license,
                            backref="objects")
    refers_to = db.relationship('JsonObject',
            secondary=lambda: association_table_jsonobject,
            primaryjoin=association_table_jsonobject.c.jsonobject_refers_to_id==id,
            secondaryjoin=association_table_jsonobject.c.jsonobject_referred_to_by_id==id,
            backref="referred_to_by")

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey('organization.id'),
                        nullable=False)
    creator_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                            nullable=False)
    schema_id = db.Column(db.Integer(), db.ForeignKey('schema.id'),
                            nullable=False)


@event.listens_for(JsonObject, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """Event listener that runs before a record is updated, and sets the
    last_updated field accordingly.
    """
    target.last_updated = datetime.utcnow()
