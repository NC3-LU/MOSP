from werkzeug.security import generate_password_hash

from mosp.models import User


def test_user(session):
    user = User(
        login="john",
        pwdhash=generate_password_hash("password"),
        email="john@mosp.localhost"
    )

    session.add(user)
    session.commit()

    assert user.is_admin is False
    assert user.is_api is False
    assert user.is_api is False
    assert user.check_password("password") is True
    assert user.apikey != ""
