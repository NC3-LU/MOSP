#! /usr/bin/env python
# -*- coding: utf-8 -

# required imports and code exection for basic functionning

import os
import errno
import logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import flask_restless
from flask_mail import Mail


def set_logging(log_path=None, log_level=logging.INFO, modules=(),
                log_format='%(asctime)s %(levelname)s %(message)s'):
    if not modules:
        modules = ('workers.fetch_cve', 'bootstrap', 'runserver', 'web',)
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


# def create_directory(directory):
#     """Creates the necessary directories (public uploads, etc.)"""
#     if not os.path.exists(directory):
#         try:
#             os.makedirs(directory)
#         except OSError as e:
#             if e.errno != errno.EEXIST:
#                 raise

# Create Flask application
application = Flask('web', instance_relative_config=True)
application.config.from_pyfile(os.environ.get(
                               'APPLICATION_SETTINGS',
                               'development.cfg'), silent=False)
db = SQLAlchemy(application)
mail = Mail(application)


# Jinja filters
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)
# def instance_domain_name(*args):
#     return request.url_root.replace('http', 'https').strip("/")

application.jinja_env.filters['datetimeformat'] = datetimeformat
# application.jinja_env.filters['instance_domain_name'] = instance_domain_name


set_logging(application.config['LOG_PATH'])

# create_directory(application.config['UPLOAD_FOLDER'])

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(application, flask_sqlalchemy_db=db)


def populate_g():
    from flask import g
    g.db = db
    g.app = application
