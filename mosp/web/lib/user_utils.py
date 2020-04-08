from itsdangerous import URLSafeTimedSerializer

from mosp.bootstrap import application


def generate_confirmation_token(login):
    serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])
    return serializer.dumps(login, salt=application.config["SECURITY_PASSWORD_SALT"])


def confirm_token(token):
    serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])
    try:
        login = serializer.loads(
            token,
            salt=application.config["SECURITY_PASSWORD_SALT"],
            max_age=application.config["TOKEN_VALIDITY_PERIOD"],
        )
    except:
        return False
    return login
