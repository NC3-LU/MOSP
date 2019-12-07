import os
import tempfile

import pytest
from werkzeug.security import generate_password_hash

# import mosp
from mosp.models import User

# @pytest.fixture
# def client():
#     db_fd, application.config['DATABASE'] = tempfile.mkstemp()
#     application.config['TESTING'] = True
#
#     with application.test_client() as client:
#         with application.app_context():
#             #mosp.init_db()
#             pass
#         yield client
#
#     os.close(db_fd)
#     os.unlink(application.config['DATABASE'])


@pytest.fixture
def some_db(create_user):
    new_user = User(login='john', pwdhash=generate_password_hash('password'))
    yield new_user

def test_rights(create_user):
    assert new_user.is_admin == False

# def test_empty_db(some_db):
#     """Start with a blank database."""
#     new_user = User(login='john', pwdhash=generate_password_hash('password'))
#     new_user.save()
#     assert new_user.is_admin == False
