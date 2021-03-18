#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy.exc
from typing import Dict, Any
from flask import request
from flask_login import current_user
from flask_restx import Namespace, Resource, fields, reqparse, abort

from mosp.bootstrap import db
from mosp.models import JsonObject
from mosp.api.common import check_information
from mosp.api.v2.common import auth_func, object_params_model, organization_params_model, metada_params_model


object_ns = Namespace("object", description="object related operations")


# Argument Parsing
parser = reqparse.RequestParser()
parser.add_argument("uuid", type=str, help="UUID of the object.")
parser.add_argument("name", type=str, help="Name of the object.")
parser.add_argument("language", type=str, help="Language of the object.")
parser.add_argument("organization", type=str, help="Organization name of the object.")
parser.add_argument("schema", type=str, help="Schema name of the object.")
parser.add_argument("page", type=int, required=False, default=1, help="Page number")
parser.add_argument("per_page", type=int, required=False, default=10, help="Page size")


# Response marshalling
object = object_ns.model("Object", object_params_model)
object["organization"] = fields.Nested(object_ns.model("Organization", organization_params_model))
metadata = object_ns.model("metadata", metada_params_model)

object_list_fields = object_ns.model(
    "ObjectsList",
    {
        "metadata": fields.Nested(
            metadata, description="Metada related to the result."
        ),
        "data": fields.List(fields.Nested(object), description="List of objects."),
    },
)


@object_ns.route("/")
class ObjectsList(Resource):
    """Create new objects."""

    @object_ns.doc("list_objects")
    @object_ns.expect(parser)
    @object_ns.marshal_list_with(object_list_fields)
    def get(self):
        """List all objects."""

        args = parser.parse_args()
        offset = args.pop("page", 1) - 1
        limit = args.pop("per_page", 10)
        object_uuid = args.pop("uuid", None)
        object_language = args.pop("language", None)
        object_organization = args.pop("organization", None)
        object_schema = args.pop("schema", None)
        args = {k: v for k, v in args.items() if v is not None}

        result = {
            "data": [],
            "metadata": {
                "count": 0,
                "offset": offset,
                "limit": limit,
            },
        }

        results = []
        count = 0
        query = JsonObject.query
        # Filter on attribute of the object
        for arg in args:
            if hasattr(JsonObject, arg):
                try:
                    query = query.filter(getattr(JsonObject, arg) == args[arg])
                except Exception:
                    pass
        # Filter on other attributes
        if object_organization:
            query = query.filter(JsonObject.organization.has(name=object_organization))
        if object_schema:
            query = query.filter(JsonObject.schema.has(name=object_schema))
        if object_uuid:
            query = query.filter(
                JsonObject.json_object[("uuid")].astext == str(object_uuid)
            )
        if object_language:
            query = query.filter(
                JsonObject.json_object[("language")].astext == object_language
            )

        total = query.count()
        query = query.limit(limit)
        results = query.offset(offset * limit)
        count = total

        result["data"] = results
        result["metadata"]["count"] = count

        return result, 200

    @object_ns.doc("create_object")
    @object_ns.expect([object])
    @object_ns.marshal_list_with(object_list_fields, code=201)
    @object_ns.response(401, "Authorization needed")
    @auth_func
    def post(self):
        """Create a new object"""
        result = {
            "data": [],
            "metadata": {"count": 0, "offset": 0, "limit": 0},
        }  # type: Dict[Any, Any]
        errors = []
        for obj in object_ns.payload:

            check_information(obj)

            try:
                new_object = JsonObject(**obj, creator_id=current_user.id)
                db.session.add(new_object)
                db.session.commit()
                result["data"].append(new_object)
                result["metadata"]["count"] += 1
            except (
                sqlalchemy.exc.IntegrityError,
                sqlalchemy.exc.InvalidRequestError,
            ) as e:
                # logger.error("Error when creatng object {}".format(object["id"]))
                errors.append(object["id"])
                db.session.rollback()

        # if some objects can not created we return the HTTP code 207 (Multi-Status)
        # if all objects of the batch POST request are created we simply return 201.
        return result, 207 if errors else 201


@object_ns.route("/<int:id>")
class ObjectItem(Resource):
    """Get object details."""

    @object_ns.doc("object_get")
    @object_ns.marshal_with(object, code=200)
    @auth_func
    def get(self, id):
        return JsonObject.query.filter(JsonObject.id == id).all(), 200

    # @object_ns.doc("object_patch")
    # @object_ns.expect(object)
    # @object_ns.marshal_with(object, code=201)
    # @auth_func
    # def patch(self, id):
    #
    #     obj = JsonObject.query.filter(JsonObject.id == id).all(), 200
    #
    #     return current_user, 201
