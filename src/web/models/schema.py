
from datetime import datetime
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import JSON

from bootstrap import db

class Schema(db.Model):
    """Represent a JSON schema.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow())
    json_schema = db.Column(JSON, default=None)

    # relationship
    objects = db.relationship('JsonObject', backref='schema', lazy='dynamic',
                               cascade='all,delete-orphan')

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey('organization.id'),
                        default=None)
    creator_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                           default=None)


    @validates('name')
    def validates_name(self, key, value):
        assert len(value) <= 100, \
            AssertionError("maximum length for name: 100")
        return value.replace(' ', '').strip()
