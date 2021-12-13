import re
import secrets
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash
from validate_email import validate_email

from mosp.bootstrap import db


association_table_organization = db.Table(
    "association_users_organizations",
    db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("organization_id", db.Integer, db.ForeignKey("organization.id")),
)


def generate_token():
    return secrets.token_urlsafe(64)


class User(db.Model, UserMixin):
    """
    Represent a user. Logins and api keys are unique, emails addresses are not.
    """

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), unique=True, nullable=False)
    pwdhash = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    apikey = db.Column(db.String(100), default=generate_token, unique=True)

    # user rights
    is_active = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), default=False)
    is_api = db.Column(db.Boolean(), default=False)

    # relationships
    organizations = db.relationship(
        "Organization",
        secondary=lambda: association_table_organization,
        backref="users",
    )
    # objects = db.relationship("JsonObject", backref="creator", lazy="dynamic")
    schemas = db.relationship("Schema", backref="creator", lazy="dynamic")

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

    def generate_apikey(self):
        self.apikey = generate_token()

    def is_organization_member(self, organization_id):
        return organization_id in [org.id for org in self.organizations]

    def __str__(self):
        return self.login

    @validates("login")
    def validates_login(self, key, value):
        assert 3 <= len(value) <= 50, AssertionError("maximum length for login: 30")
        return re.sub("[^a-zA-Z0-9_-]", "", value.strip())

    @validates("email")
    def validates_email(self, key, value):
        assert 3 <= len(value) <= 256, AssertionError("maximum length for email: 256")
        if validate_email(value):
            return value

    @validates("apikey")
    def validates_apikey(self, key, value):
        assert 30 <= len(value) <= 100, AssertionError("minimum length for apikey: 30")

    @staticmethod
    def make_valid_login(login):
        return re.sub("[^a-zA-Z0-9_-]", "", login)
