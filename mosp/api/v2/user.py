#! /usr/bin/env python
# -*- coding: utf-8 -*-

import secrets
import sqlalchemy
from werkzeug.security import generate_password_hash
from flask import request
from flask_login import current_user
from flask_restx import Namespace, Resource, fields, reqparse, abort
from flask_restx.inputs import date_from_iso8601

import mosp.scripts
from mosp.bootstrap import db
from mosp.models import User, Organization
from mosp.notifications import notifications
from mosp.api.v2.common import (
    auth_func,
    user_params_model,
    metada_params_model,
    organization_params_model,
)


user_ns = Namespace("user", description="user related operations")


# Argument Parsing
parser = reqparse.RequestParser()
parser.add_argument("login", type=str, help="The name of the organization.")
parser.add_argument(
    "created_at",
    type=date_from_iso8601,
    required=False,
    help="The date of creation of the user.",
)
parser.add_argument(
    "last_seen",
    type=date_from_iso8601,
    required=False,
    help="The date of last connection of the user.",
)
parser.add_argument("page", type=int, required=False, default=1, help="Page number")
parser.add_argument("per_page", type=int, required=False, default=10, help="Page size")


# Response marshalling
user = user_ns.model("User", user_params_model)
user["organizations"] = fields.List(
    fields.Nested(user_ns.model("Organization", organization_params_model)),
    description="List of organizations.",
)
metadata = user_ns.model("metadata", metada_params_model)
users_list_fields = user_ns.model(
    "UsersList",
    {
        "metadata": fields.Nested(
            metadata, description="Metada related to the result."
        ),
        "data": fields.List(fields.Nested(user), description="List of users."),
    },
)

create_user_model = user_ns.model(
    "User",
    {
        "login": fields.String(description="The user login."),
        "email": fields.String(description="The user login."),
        "org_id": fields.Integer(
            description="The id of an organization which has no membership restriction."
        ),
        "apikey": fields.String(description="The user login.", readonly=True),
        "organizations": fields.List(
            fields.Nested(user_ns.model("Organization", organization_params_model)),
            description="List of organizations.",
            readonly=True,
        ),
    },
)


@user_ns.route("/")
class UsersList(Resource):
    """List all users."""

    @user_ns.doc("list_users")
    @user_ns.expect(parser)
    @user_ns.marshal_list_with(users_list_fields)
    @auth_func
    def get(self):
        """List all users."""

        args = parser.parse_args()
        offset = args.pop("page", 1) - 1
        limit = args.pop("per_page", 10)
        args = {k: v for k, v in args.items() if v is not None}

        result = {
            "data": [],
            "metadata": {
                "count": 0,
                "offset": offset,
                "limit": limit,
            },
        }

        try:
            query = User.query
            for arg in args:
                if hasattr(User, arg):
                    query = query.filter(getattr(User, arg) == args[arg])
            total = query.count()
            query = query.limit(limit)
            results = query.offset(offset * limit)
            count = total
        except Exception as e:
            print(e)

        result["data"] = results
        result["metadata"]["count"] = count

        return result, 200

    @user_ns.doc("user_create")
    @user_ns.expect(create_user_model)
    @user_ns.marshal_with(create_user_model, skip_none=True, code=201)
    def post(self):
        """Create, without authentication, a new deactivated user."""
        org_id_auto_join = user_ns.payload.pop("org_id", None)

        new_user = None
        try:
            new_user = User(
                **user_ns.payload,
                pwdhash=generate_password_hash(""),
                is_active=False,
                is_admin=False,
            )
            db.session.add(new_user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return abort(409, "Login already used.")
        except Exception:
            db.session.rollback()
            return abort(403)

        # when creating an account, a user can directly join an organization
        # which has no membership restriction
        if new_user and org_id_auto_join:
            # check if the organization exists and is without membership
            # restriction
            org_object = (
                Organization.query.filter(
                    Organization.is_membership_restricted == False
                )
                .filter(Organization.id == org_id_auto_join)
                .first()
            )
            if org_object:
                new_user.organizations.append(org_object)
                db.session.commit()

        if new_user:
            notifications.confirm_account(new_user)

        return [new_user], 201


@user_ns.route("/<int:id>")
class UserItem(Resource):
    """Get user."""

    @user_ns.doc("user_get")
    @user_ns.marshal_with(user, code=200)
    @auth_func
    def get(self, id):
        """Get details about the user with the specified id."""

        return User.query.filter(User.id == id).all(), 200


@user_ns.route("/me")
class UserSelfItem(Resource):
    """Return known information about the requestor."""

    @user_ns.doc("client_self")
    @user_ns.marshal_with(user, code=200)
    @auth_func
    def get(self):
        """Return known information about the authenticated requestor."""

        return current_user, 200


@user_ns.route("/me/regenerate-token")
class UserRegenerateToken(Resource):
    """Return a new token for the user."""

    @user_ns.doc("user_regenerate_token")
    @auth_func
    def get(self):
        """Return a new token for the user."""

        current_user.apikey = secrets.token_urlsafe(64)
        db.session.commit()
        return {"api-key": current_user.apikey}, 200
