#! /usr/bin/python
#-*- coding:utf-8 -*

from werkzeug.security import generate_password_hash

from bootstrap import db
from models import User


def create_user(login, password, is_admin):
    """Creates a normal user or an administrator.
    """
    user = User(login=login,
                pwdhash=generate_password_hash(password),
                is_active=True,
                is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
