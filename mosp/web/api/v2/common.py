#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask_restx import abort

from mosp.models import User
from mosp.web.views.common import login_user_bundle


def auth_func(func):
    def wrapper(*args, **kwargs):
        if "X-API-KEY" in request.headers:
            token = request.headers.get("X-API-KEY", False)
            if token:
                user = User.query.filter(User.apikey == token).first()
                login_user_bundle(user)
                if not user:
                    abort(401, Error="Authentication required.")
        else:
            abort(401, Error="Authentication required.")
        return func(*args, **kwargs)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper
