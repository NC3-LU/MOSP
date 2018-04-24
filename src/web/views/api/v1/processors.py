#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from flask import request
from flask_login import current_user
from flask_restless import ProcessingException

from web.views.common import login_user_bundle
from web.models import User

logger = logging.getLogger(__name__)

def auth_func(*args, **kw):
    if request.authorization:
        user = User.query.filter(User.login == request.authorization.username).first()
        if not user:
            raise ProcessingException("Couldn't authenticate your user",
                                      code=401)
        if not user.check_password(request.authorization.password):
            raise ProcessingException("Couldn't authenticate your user",
                                      code=401)
        if not user.is_active:
            raise ProcessingException("Couldn't authenticate your user", code=401)
        login_user_bundle(user)
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not authenticated!', code=401)
