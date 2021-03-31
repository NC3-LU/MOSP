HOST = "127.0.0.1"
PORT = 5000
DEBUG = True
TESTING = True
INSTANCE_URL = "http://127.0.0.1:5000"

DB_CONFIG_DICT = {
    "user": "pgsqluser",
    "password": "pgsqlpwd",
    "host": "localhost",
    "port": 5432,
}
DATABASE_NAME = "mosp"
SQLALCHEMY_DATABASE_URI = "postgres://{user}:{password}@{host}:{port}/{name}".format(
    name=DATABASE_NAME, **DB_CONFIG_DICT
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = "dev"
SECURITY_PASSWORD_SALT = "dev"

SELF_REGISTRATION = True

UPLOAD_FOLDER = "./mosp/web/public/pictures/"
ALLOWED_EXTENSIONS = set(["png"])

ADMIN_EMAIL = "info@cases.lu"
ADMIN_URL = "https://www.cases.lu"

LOG_PATH = "./var/log/mosp.log"
LOG_LEVEL = "info"

CSRF_ENABLED = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

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
