
from werkzeug.security import generate_password_hash

from mosp.models import User


def test_user(session):
    user = User(login='john', pwdhash=generate_password_hash('password'))

    session.add(user)
    session.commit()

    assert user.is_admin == False
    assert user.is_api == False
    assert user.is_api == False
    assert user.public_profile == True
    assert user.check_password('password') == True
