#! /usr/bin/env python
# required imports and code exection for basic functionning
import logging
import os
import re
import uuid
from typing import Union

from flask import Flask
from flask import g
from flask import request
from flask_babel import Babel
from flask_babel import format_datetime
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.routing import BaseConverter
from werkzeug.routing import ValidationError


def set_logging(
    log_path=None,
    log_level=logging.INFO,
    modules=(),
    log_format="%(asctime)s %(levelname)s %(message)s",
):
    if not modules:
        modules = (
            "bootstrap",
            "runserver",
            "web",
        )
    handler: Union[logging.Handler, None] = None
    if log_path:
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        if not os.path.exists(log_path):
            open(log_path, "w").close()
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
application = Flask(__name__, instance_relative_config=True)

# Loads the appropriate configuration
ON_HEROKU = int(os.environ.get("HEROKU", 0)) == 1
TESTING = os.environ.get("testing", "") == "actions"
if TESTING:
    # Testing on GitHub Actions
    application.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://mosp:password@localhost:5432/mosp"
elif ON_HEROKU:
    # Deployment on Heroku
    application.config.from_pyfile("heroku.py", silent=False)
elif os.environ.get("MOSP_CONFIG", ""):
    # if a specific configuration is provided by the user
    # this does not works with mod_wsgi
    config_file = os.environ.get("MOSP_CONFIG", "")
    application.config.from_pyfile(config_file, silent=False)
else:
    try:
        application.config.from_pyfile("production.py", silent=False)
    except Exception:
        application.config.from_pyfile("development.py", silent=False)

db = SQLAlchemy(application)
migrate = Migrate(application, db)


cors = CORS(
    application,
    resources={
        r"/schema/def/*": {"origins": "*"},
        r"/api/v2/*": {"origins": "*"},
    },
)


# i18n and l10n support
def get_locale():
    # if a user is logged in, use the locale from the user settings
    # user = getattr(g, 'user', None)
    # if user is not None:
    #     return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(
        ["fr", "en", "de", "es", "it", "nl", "ru", "ro"]
    )


def get_timezone():
    user = getattr(g, "user", None)
    if user is not None:
        return user.timezone


babel = Babel(application, locale_selector=get_locale, timezone_selector=get_timezone)


# Jinja filters
def datetimeformat(value, format="%Y-%m-%d %H:%M"):
    return value.strftime(format)


# def instance_domain_name(*args):
#     return request.url_root.replace('http', 'https').strip("/")


application.jinja_env.filters["datetimeformat"] = datetimeformat
application.jinja_env.filters["datetime"] = format_datetime
# application.jinja_env.filters['instance_domain_name'] = instance_domain_name

# URL Converters
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class UUIDConverter(BaseConverter):
    """
    UUID converter for the Werkzeug routing system.
    """

    def __init__(self, map, strict=True):
        super().__init__(map)
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


application.url_map.converters["uuid"] = UUIDConverter

if application.config.get("LOG_PATH", ""):
    set_logging(application.config["LOG_PATH"])
