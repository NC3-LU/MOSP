import pytest

import app as _app_module  # noqa: F401 — registers all blueprints on the application

from mosp.bootstrap import application
from mosp.bootstrap import db as _db


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    app = application

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope="session")
def db(app, request):
    """Session-wide test database."""

    def teardown():
        _db.drop_all()

    _db.app = app
    # _db.init_app(_db.app)
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def session(db, request):
    """Creates a new database session for a test.

    Data is committed to the real DB so that the Flask test client (which
    opens its own DB connection per request) can see it.  All rows inserted
    during the test are deleted in teardown via a TRUNCATE … CASCADE so that
    tests remain isolated from each other.
    """
    yield db.session

    # Teardown: remove all rows from every table in reverse dependency order.
    db.session.remove()
    with db.engine.begin() as conn:
        table_names = ", ".join(
            '"{}"'.format(t.name)
            for t in reversed(db.metadata.sorted_tables)
            if t.name != "alembic_version"
        )
        if table_names:
            conn.execute(
                db.text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
            )


@pytest.fixture(scope="function")
def client(app, session):
    """Test HTTP client with CSRF disabled.

    Depends on ``session`` so that the DB TRUNCATE teardown always runs
    *after* the client is closed, keeping test isolation intact.

    In Flask 3.x, ``g`` is scoped to the application context rather than
    the request context.  Because the ``app`` fixture pushes a single
    session-wide application context, ``g._login_user`` (set by
    Flask-Login) would otherwise persist across tests.  Pushing a fresh
    application context here gives every test its own ``g`` so that login
    state cannot bleed between tests.
    """
    app.config["WTF_CSRF_ENABLED"] = False
    # Push a fresh app context so that Flask's g (and g._login_user) is
    # isolated to this test, not shared with the session-wide app context.
    ctx = app.app_context()
    ctx.push()
    try:
        with app.test_client() as c:
            yield c
    finally:
        ctx.pop()
        app.config["WTF_CSRF_ENABLED"] = True
