#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask_restx import Namespace, Resource, fields, reqparse, abort
from flask_restx.inputs import date_from_iso8601

from mosp.bootstrap import db
from mosp.models import User
from mosp.web.views.api.v2.common import auth_func


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
organization = user_ns.model(
    "Organization",
    {
        "id": fields.Integer(description="Organization id."),
        "name": fields.String(description="The organization name."),
        "description": fields.String(description="The organization description."),
        "organization_type": fields.String(description="The type of the organization."),
        "last_updated": fields.DateTime(description="Updated time of the schema."),
    },
)

user = user_ns.model(
    "User",
    {
        "id": fields.Integer(description="User id."),
        "login": fields.String(description="The user login."),
        "created_at": fields.DateTime(description="The date of creation of the user."),
        "last_seen": fields.DateTime(description="The date of last connection of the user."),
        "organizations": fields.List(fields.Nested(organization), description="List of organizations."),
    },
)

metadata = user_ns.model(
    "metadata",
    {
        "count": fields.String(
            readonly=True, description="Total number of the items of the data."
        ),
        "offset": fields.String(
            readonly=True,
            description="Position of the first element of the data from the total data amount.",
        ),
        "limit": fields.String(readonly=True, description="Requested limit data."),
    },
)

users_list_fields = user_ns.model(
    "UsersList",
    {
        "metadata": fields.Nested(
            metadata, description="Metada related to the result."
        ),
        "data": fields.List(fields.Nested(user), description="List of users."),
    },
)


@user_ns.route("/")
class UsersList(Resource):
    """."""

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

    # @user_ns.doc("create_organization")
    # @user_ns.expect(organization)
    # @user_ns.marshal_with(organization, code=201)
    # @auth_func
    # def post(self):
    #     """Create a new organization."""
    #     new_schema = Organization(**user_ns.payload)
    #     db.session.add(new_schema)
    #     db.session.commit()
    #     return new_schema, 201


@user_ns.route("/<int:id>")
class UserItem(Resource):
    """Get user details."""

    @user_ns.doc("user_get")
    @user_ns.marshal_with(user, code=200)
    @auth_func
    def get(self, id):
        return User.query.filter(User.id == id).all(), 200
