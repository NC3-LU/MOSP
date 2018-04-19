import re
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import validates
from werkzeug import check_password_hash

from bootstrap import db


class User(db.Model, UserMixin):
    """
    Represent a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(), unique=True, nullable=False)
    pwdhash = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow())
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())

    public_profile = db.Column(db.Boolean(), default=True)

    # user rights
    is_active = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), default=False)
    is_api = db.Column(db.Boolean(), default=False)

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey('organization.id'),
                           default=None)


    def get_id(self):
        """
        Return the id of the user.
        """
        return self.id

    def check_password(self, password):
        """
        Check the password of the user.
        """
        return check_password_hash(self.pwdhash, password)

    @validates('login')
    def validates_login(self, key, value):
        assert 3 <= len(value) <= 30, \
            AssertionError("maximum length for login: 30")
        return re.sub('[^a-zA-Z0-9_\.]', '', value.strip())
