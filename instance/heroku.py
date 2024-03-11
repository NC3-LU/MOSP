import os

HOST = "0.0.0.0"
PORT = os.environ.get("PORT")
TESTING = False
INSTANCE_URL = "http://127.0.0.1:5000"

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace("://", "ql://", 1)
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = "SECRET KEY"
SECURITY_PASSWORD_SALT = "SECURITY PASSWORD SALT"

SELF_REGISTRATION = True

LOG_PATH = "mosp.log"
LOG_LEVEL = "info"

CSRF_ENABLED = True

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_URL = os.environ.get("ADMIN_URL")

LOG_PATH = ""
