#! /usr/bin/python
from werkzeug.security import generate_password_hash

from mosp.bootstrap import db
from mosp.models import User


def create_user(login, email, password, is_active, is_admin):
    """Creates a normal user or an administrator."""
    user = User(
        login=login,
        email=email,
        pwdhash=generate_password_hash(password),
        is_active=is_active,
        is_admin=is_admin,
    )
    try:
        db.session.add(user)
        db.session.commit()
        return user
    except Exception:
        db.session.rollback()
