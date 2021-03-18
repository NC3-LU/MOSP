#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask_restx import Namespace, Resource, fields, reqparse, abort

from mosp.bootstrap import db
from mosp.models import Schema
from mosp.api.v2.common import schema_params_model


schema_ns = Namespace("schema", description="schema related operations")


# Argument Parsing
parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="The name of the organization.")
parser.add_argument("organization_type", type=str, help="The type of the organization.")
parser.add_argument("page", type=int, required=False, default=1, help="Page number")
parser.add_argument("per_page", type=int, required=False, default=10, help="Page size")


# Response marshalling
schema = schema_ns.model("Schema", schema_params_model)
metadata = schema_ns.model(
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

schema_list_fields = schema_ns.model(
    "SchemasList",
    {
        "metadata": fields.Nested(
            metadata, description="Metada related to the result."
        ),
        "data": fields.List(fields.Nested(schema), description="List of schemas."),
    },
)


@schema_ns.route("/")
class SchemasList(Resource):
    """Create new schema."""

    @schema_ns.doc("list_schemas")
    @schema_ns.expect(parser)
    @schema_ns.marshal_list_with(schema_list_fields)
    def get(self):
        """List all schemas."""

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
            query = Schema.query
            for arg in args:
                if hasattr(Schema, arg):
                    query = query.filter(getattr(Schema, arg) == args[arg])
            total = query.count()
            query = query.limit(limit)
            results = query.offset(offset * limit)
            count = total
        except Exception as e:
            print(e)

        result["data"] = results
        result["metadata"]["count"] = count

        return result, 200

    # @schema_ns.doc("create_organization")
    # @schema_ns.expect(organization)
    # @schema_ns.marshal_with(organization, code=201)
    # @auth_func
    # def post(self):
    #     """Create a new organization."""
    #     new_schema = Organization(**schema_ns.payload)
    #     db.session.add(new_schema)
    #     db.session.commit()
    #     return new_schema, 201
