#!/usr/bin/env python
import os

# Webserver
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "0") == "1"
TESTING = os.getenv("TESTING", "0") == "1"

INSTANCE_URL = "http://127.0.0.1:5000"

DB_HOSTNAME = os.getenv("DB_HOSTNAME", "db")
DB_NAME = os.getenv("DB_NAME", "mosp")
DB_USERNAME = os.getenv("DB_USERNAME", "mosp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mosp")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

# Database
DB_CONFIG_DICT = {
    "host": DB_HOSTNAME,
    "user": DB_USERNAME,
    "password": DB_PASSWORD,
    "port": DB_PORT,
}
DATABASE_NAME = DB_NAME
SQLALCHEMY_DATABASE_URI = "postgresql://{user}:{password}@{host}:{port}/{name}".format(
    name=DATABASE_NAME, **DB_CONFIG_DICT
)
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "0") == "1"

SECRET_KEY = "LCx3BchmHRxFzkEv4BqQJyeXRLXenf"
SECURITY_PASSWORD_SALT = "L8gTsyrpRQEF8jNWQPyvRfv7U5kJkD"

LOG_PATH = "./var/log/mosp.log"
LOG_LEVEL = "info"

UPLOAD_FOLDER = "./mosp/web/public/pictures/"
ALLOWED_EXTENSIONS = {"png"}

ADMIN_EMAIL = "opensource@nc3.lu"
ADMIN_URL = "https://www.nc3.lu"

MAX_CONTENT_LENGTH = 16 * 1024 * 1024

SELF_REGISTRATION = True

# Notification
MAIL_SERVER = "localhost"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = DEBUG
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = "admin@admin.localhost"
TOKEN_VALIDITY_PERIOD = 3600
