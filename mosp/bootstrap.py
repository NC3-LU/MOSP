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
from flask_wtf.csrf import CSRFProtect
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
            "app",
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
    # Minimal defaults so the app (incl. API v2 setup) imports cleanly
    # without requiring a real instance config file.
    # Direct assignment (not setdefault) because Flask's default_config
    # seeds SECRET_KEY/TESTING with None/False, which would make setdefault
    # a silent no-op.
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    application.config["SECRET_KEY"] = "testing-only-not-a-real-secret"
    application.config["SECURITY_PASSWORD_SALT"] = "testing-only-not-a-real-salt"
    application.config["ADMIN_EMAIL"] = "admin@test.local"
    application.config["ADMIN_URL"] = "http://test.local"
    application.config["INSTANCE_URL"] = "http://test.local"
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

_KNOWN_WEAK_KEYS = {
    "",
    "dev",
    "SECRET KEY",
    "SECURITY PASSWORD SALT",
    "LCx3BchmHRxFzkEv4BqQJyeXRLXenf",
    "L8gTsyrpRQEF8jNWQPyvRfv7U5kJkD",  # old SECURITY_PASSWORD_SALT default
}

if not application.config.get("TESTING") and os.environ.get("testing") != "actions":
    if application.config.get("SECRET_KEY", "") in _KNOWN_WEAK_KEYS:
        raise RuntimeError(
            "SECRET_KEY is not set or uses a known insecure default. "
            "Set the SECRET_KEY environment variable to a strong random value "
            '(e.g. python -c "import secrets; print(secrets.token_hex(32))").'
        )
    if application.config.get("SECURITY_PASSWORD_SALT", "") in _KNOWN_WEAK_KEYS:
        raise RuntimeError(
            "SECURITY_PASSWORD_SALT is not set or uses a known insecure default. "
            "Set the SECURITY_PASSWORD_SALT environment variable."
        )

# Database and migration
db = SQLAlchemy(application)
migrate = Migrate(application, db)

# Enable CSRF protection globally
csrf = CSRFProtect(application)

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
