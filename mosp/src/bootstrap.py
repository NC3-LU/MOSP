#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import re
import os
import uuid
import logging
import flask_restless
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, format_datetime
from werkzeug.routing import BaseConverter, ValidationError


def set_logging(log_path=None, log_level=logging.INFO, modules=(),
                log_format='%(asctime)s %(levelname)s %(message)s'):
    if not modules:
        modules = ('bootstrap', 'runserver', 'web',)
    if log_path:
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        if not os.path.exists(log_path):
            open(log_path, 'w').close()
        handler = logging.FileHandler(log_path)
    else:
        handler = logging.StreamHandler()
    formater = logging.Formatter(log_format)
    handler.setFormatter(formater)
    for logger_name in modules:
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)
        for handler in logger.handlers:
            handler.setLevel(log_level)
        logger.setLevel(log_level)


# Create Flask application
application = Flask('web', instance_relative_config=True)
try:
    application.config.from_pyfile('production.cfg', silent=False)
except Exception:
    application.config.from_pyfile('development.cfg', silent=False)
db = SQLAlchemy(application)


babel = Babel(application)
@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    # user = getattr(g, 'user', None)
    # if user is not None:
    #     return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['fr', 'en'])

# @babel.timezoneselector
# def get_timezone():
#     user = getattr(g, 'user', None)
#     if user is not None:
#         return user.timezone


# Jinja filters
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)
# def instance_domain_name(*args):
#     return request.url_root.replace('http', 'https').strip("/")

application.jinja_env.filters['datetimeformat'] = datetimeformat
application.jinja_env.filters['datetime'] = format_datetime
# application.jinja_env.filters['instance_domain_name'] = instance_domain_name

# URL Converters
UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
class UUIDConverter(BaseConverter):
    """
    UUID converter for the Werkzeug routing system.
    """
    def __init__(self, map, strict=True):
        super(UUIDConverter, self).__init__(map)
        self.strict = strict


    def to_python(self, value):
        if self.strict and not UUID_RE.match(value):
            raise ValidationError()
        try:
            return uuid.UUID(value)
        except ValueError:
            raise ValidationError()


    def to_url(self, value):
        return str(value)


application.url_map.converters['uuid'] = UUIDConverter

# set_logging(application.config['LOG_PATH'])

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(application, flask_sqlalchemy_db=db)


def populate_g():
    from flask import g
    g.db = db
    g.app = application
