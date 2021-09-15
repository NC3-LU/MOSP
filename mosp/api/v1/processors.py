#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from flask import request
from flask_login import current_user
from flask_restless import ProcessingException

from mosp.models import User
from mosp.views.common import login_user_bundle

logger = logging.getLogger(__name__)


def auth_func(*args, **kw):
    """
    Pre-processor used to check if a user is authenticated.
    """
    if current_user.is_authenticated:
        return

    user = None
    if request.headers.get("Authorization", False):
        token = request.headers.get("Authorization").split(" ")[1]
        user = User.query.filter(User.apikey == token).first()

    if request.authorization:
        user = User.query.filter(User.login == request.authorization.username).first()
        if user and not user.check_password(request.authorization.password):
            raise ProcessingException("Couldn't authenticate your user", code=401)

    if not user:
        raise ProcessingException("Couldn't authenticate your user", code=401)
    if not user.is_active:
        raise ProcessingException("Couldn't authenticate your user", code=401)

    login_user_bundle(user)
