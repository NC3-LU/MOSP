import json

import pytest
from werkzeug.security import generate_password_hash

from mosp.bootstrap import db
from mosp.models import JsonObject
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


def test_owner_can_get_delete_warning_page(client, session):
    org = make_org(session, "OrgA_del2")
    owner = make_user(session, "owner_d2", "owner_d2@t.local", org=org)
    schema = make_schema(session, "Schema_d2", org, creator_id=owner.id)

    login_as(client, "owner_d2")
    response = client.get(f"/schema/delete/{schema.id}")
    assert response.status_code == 200
    assert b"Schema_d2" in response.data


def test_non_owner_cannot_post_delete_schema(client, session):
    org_a = make_org(session, "OrgA_del3")
    org_b = make_org(session, "OrgB_del3")
    owner = make_user(session, "owner_d3", "owner_d3@t.local", org=org_a)
    make_user(session, "other_d3", "other_d3@t.local", org=org_b)
    schema = make_schema(session, "Schema_d3", org_a, creator_id=owner.id)

    login_as(client, "other_d3")
    response = client.post(f"/schema/delete/{schema.id}")
    assert response.status_code == 403
    # Schema should still exist
    assert db.session.get(Schema, schema.id) is not None


def test_owner_post_delete_removes_schema(client, session):
    org = make_org(session, "OrgA_del4")
    owner = make_user(session, "owner_d4", "owner_d4@t.local", org=org)
    schema = make_schema(session, "Schema_d4", org, creator_id=owner.id)
    schema_id = schema.id

    login_as(client, "owner_d4")
    response = client.post(f"/schema/delete/{schema_id}", follow_redirects=False)
    assert response.status_code == 302
    assert "/schemas/" in response.headers["Location"]
    # Schema must no longer exist in the database
    assert db.session.get(Schema, schema_id) is None


# ── Fork tests ────────────────────────────────────────────────────────────────

def test_fork_creates_new_schema_with_provenance(client, session):
    org_src = make_org(session, "OrgSrc_fork")
    org_dst = make_org(session, "OrgDst_fork")
    creator = make_user(session, "creator_f1", "creator_f1@t.local", org=org_src)
    forker = make_user(session, "forker_f1", "forker_f1@t.local", org=org_dst)
    source = make_schema(session, "SourceSchema_f1", org_src, creator_id=creator.id)

    login_as(client, "forker_f1")
    response = client.post(
        f"/schema/fork/{source.id}",
        data={"org_id": org_dst.id},
        follow_redirects=False,
    )
    assert response.status_code == 302

    # A new schema should exist with forked_from_id pointing to the source
    forked = Schema.query.filter(Schema.forked_from_id == source.id).first()
    assert forked is not None
    assert forked.org_id == org_dst.id
    assert forked.creator_id == forker.id


def test_fork_unauthenticated_redirects_to_login(client, session):
    org = make_org(session, "OrgAnon_fork")
    creator = make_user(session, "creator_f2", "creator_f2@t.local", org=org)
    source = make_schema(session, "SourceSchema_f2", org, creator_id=creator.id)

    response = client.post(
        f"/schema/fork/{source.id}",
        data={"org_id": org.id},
        follow_redirects=False,
    )
    # Flask-Login redirects unauthenticated users to the login page
    assert response.status_code == 302
    assert "login" in response.headers["Location"].lower()


def test_fork_into_non_member_org_is_rejected(client, session):
    org_src = make_org(session, "OrgSrc_forkbad")
    org_other = make_org(session, "OrgOther_forkbad")
    creator = make_user(session, "creator_f3", "creator_f3@t.local", org=org_src)
    # forker_f3 belongs to org_src only, not org_other
    make_user(session, "forker_f3", "forker_f3@t.local", org=org_src)
    source = make_schema(session, "SourceSchema_f3", org_src, creator_id=creator.id)

    login_as(client, "forker_f3")
    response = client.post(
        f"/schema/fork/{source.id}",
        data={"org_id": org_other.id},
        follow_redirects=False,
    )
    assert response.status_code == 403
    # No fork should have been created
    assert Schema.query.filter(Schema.forked_from_id == source.id).first() is None
