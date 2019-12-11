import os
import tempfile

import pytest
from flask import Flask
from werkzeug.security import generate_password_hash

from mosp.models import db_init
# from mosp.bootstrap import application
from mosp.bootstrap import db as _db

from mosp.models import User





@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgres://mosp:password@localhost:54332/mosp'
    }
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://mosp:password@localhost:54332/mosp'

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""

    def teardown():
        _db.drop_all()

    _db.app = app
    _db.init_app(_db.app)
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


def test_user(session):
    user = User(login='john', pwdhash=generate_password_hash('password'))

    session.add(user)
    session.commit()

    assert user.is_admin == False



#
# @pytest.fixture
# def client():
#     db_fd, application.config['DATABASE'] = tempfile.mkstemp()
#     application.config['TESTING'] = True
#
#     with application.test_client() as client:
#         with application.app_context():
#             db_init(db)
#         yield client
#
#     os.close(db_fd)
#     os.unlink(application.config['DATABASE'])


# @pytest.fixture
# def new_user(client):
#     user = User(login='john1', pwdhash=generate_password_hash('password'))
#     client.session.add(user)
#     client.session.commit()
#     yield user
#
# def test_rights(new_user):
#     assert new_user.is_admin == False
