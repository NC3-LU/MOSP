#! /usr/bin/python
#-*- coding:utf-8 -*

from werkzeug import generate_password_hash

from web.models import User
from bootstrap import db

def create_user(login, password, is_admin):
    user = User(login=login,
                pwdhash=generate_password_hash(password),
                is_active=True,
                is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
