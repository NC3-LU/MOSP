import json

import pytest
from werkzeug.security import generate_password_hash

from mosp.models import Organization
from mosp.models import Schema
from mosp.models import User


# ── helpers ──────────────────────────────────────────────────────────────────

def make_org(session, name):
    org = Organization(name=name, description="test")
    session.add(org)
    session.commit()
    return org


def make_user(session, login, email, org=None, is_admin=False):
    user = User(
        login=login,
        pwdhash=generate_password_hash("password"),
        email=email,
        is_active=True,
        is_admin=is_admin,
    )
    if org:
        user.organizations.append(org)
    session.add(user)
    session.commit()
    return user


def make_schema(session, name, org, creator_id=None):
    schema = Schema(
        name=name,
        description="test schema",
        json_schema={"type": "object", "properties": {}},
        org_id=org.id,
        creator_id=creator_id,
    )
    session.add(schema)
    session.commit()
    return schema


def login_as(client, login_name):
    return client.post(
        "/login",
        data={"login": login_name, "password": "password"},
        follow_redirects=True,
    )


# ── GET edit / ownership tests ────────────────────────────────────────────────

def test_non_owner_cannot_edit_schema(client, session):
    org_a = make_org(session, "OrgA_edit")
    org_b = make_org(session, "OrgB_edit")
    owner = make_user(session, "owner_e1", "owner_e1@t.local", org=org_a)
    make_user(session, "other_e1", "other_e1@t.local", org=org_b)
    schema = make_schema(session, "Schema_e1", org_a, creator_id=owner.id)

    login_as(client, "other_e1")
    response = client.get(f"/schema/edit/{schema.id}")
    assert response.status_code == 403


def test_owner_can_edit_schema(client, session):
    org = make_org(session, "OrgA_edit2")
    owner = make_user(session, "owner_e2", "owner_e2@t.local", org=org)
    schema = make_schema(session, "Schema_e2", org, creator_id=owner.id)

    login_as(client, "owner_e2")
    response = client.get(f"/schema/edit/{schema.id}")
    assert response.status_code == 200


def test_edit_nonexistent_schema_returns_404(client, session):
    org = make_org(session, "Org_404")
    make_user(session, "user_404", "user_404@t.local", org=org)

    login_as(client, "user_404")
    response = client.get("/schema/edit/999999")
    assert response.status_code == 404


def test_admin_can_edit_any_schema(client, session):
    org = make_org(session, "OrgA_admin")
    owner = make_user(session, "owner_adm", "owner_adm@t.local", org=org)
    schema = make_schema(session, "Schema_adm", org, creator_id=owner.id)
    make_user(session, "admin_adm", "admin_adm@t.local", is_admin=True)

    login_as(client, "admin_adm")
    response = client.get(f"/schema/edit/{schema.id}")
    assert response.status_code == 200


# ── POST edit protection ──────────────────────────────────────────────────────

def test_non_owner_cannot_post_edit_schema(client, session):
    org_a = make_org(session, "OrgA_post")
    org_b = make_org(session, "OrgB_post")
    owner = make_user(session, "owner_p1", "owner_p1@t.local", org=org_a)
    make_user(session, "other_p1", "other_p1@t.local", org=org_b)
    schema = make_schema(session, "Schema_p1", org_a, creator_id=owner.id)

    login_as(client, "other_p1")
    response = client.post(
        f"/schema/edit/{schema.id}",
        data={
            "name": "hacked",
            "description": "hacked",
            "json_schema": json.dumps({"type": "object", "properties": {}}),
            "org_id": org_a.id,
        },
    )
    assert response.status_code == 403


# ── DELETE ownership tests ────────────────────────────────────────────────────

def test_non_owner_cannot_delete_schema(client, session):
    org_a = make_org(session, "OrgA_del")
    org_b = make_org(session, "OrgB_del")
    owner = make_user(session, "owner_d1", "owner_d1@t.local", org=org_a)
    make_user(session, "other_d1", "other_d1@t.local", org=org_b)
    schema = make_schema(session, "Schema_d1", org_a, creator_id=owner.id)

    login_as(client, "other_d1")
    response = client.get(f"/schema/delete/{schema.id}")
    assert response.status_code == 403
