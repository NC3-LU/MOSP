#! /usr/bin/env python
import logging
from typing import List

import sqlalchemy.exc
from flask import request
from flask_login import current_user
from flask_restx import fields
from flask_restx import Namespace
from flask_restx import reqparse
from flask_restx import Resource

from mosp.api.common import check_submitted_object
from mosp.api.common import create_new_version
from mosp.api.v2.common import auth_func
from mosp.api.v2.common import license_params_model
from mosp.api.v2.common import metada_params_model
from mosp.api.v2.common import object_params_model
from mosp.api.v2.common import organization_params_model
from mosp.api.v2.common import schema_params_model
from mosp.api.v2.common import uuid_type
from mosp.api.v2.types import ResultType
from mosp.bootstrap import db
from mosp.models import Event
from mosp.models import JsonObject
from mosp.models import License
from mosp.models import Schema

logger = logging.getLogger(__name__)

object_ns = Namespace("object", description="object related operations")


# Argument Parsing
parser = reqparse.RequestParser()
parser.add_argument("uuid", type=str, help="UUID of the object.")
parser.add_argument("name", type=str, help="Name of the object.")
parser.add_argument(
    "name_ilike", required=False, type=str, help="Part of the name of the object."
)
parser.add_argument("language", type=str, help="Language of the object.")
parser.add_argument("organization", type=str, help="Organization name of the object.")
parser.add_argument("schema", type=str, help="Schema name of the object.")
parser.add_argument("schema_uuid", type=uuid_type, help="Schema UUID of the object.")
parser.add_argument("page", type=int, required=False, default=1, help="Page number")
parser.add_argument("per_page", type=int, required=False, default=10, help="Page size")


# Response marshalling
object = object_ns.model("Object", object_params_model)
object["organization"] = fields.Nested(
    object_ns.model("Organization", organization_params_model), readonly=True
)
object["licenses"] = fields.List(
    fields.Nested(object_ns.model("License", license_params_model)),
    description="List of licenses.",
)
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

# Marshalling for GET/<id> (single element); also returns the schema
object_get_id = object_ns.model("Object", object_params_model)
object_get_id["organization"] = fields.Nested(
    object_ns.model("Organization", organization_params_model), readonly=True
)
object_get_id["schema"] = fields.Nested(
    object_ns.model("Schema", schema_params_model), readonly=True
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
        object_schema_uuid = args.pop("schema_uuid", None)
        name_ilike = args.pop("name_ilike")
        args = {k: v for k, v in args.items() if v is not None}

        result: ResultType = {
            "data": [],
            "metadata": {
                "count": 0,
                "offset": offset,
                "limit": limit,
            },
        }

        # Log the event
        new_event = Event(
            scope="JsonObject",
            subject="id={} uuid={} schema_uuid={}".format(
                "", str(object_uuid), str(object_schema_uuid)
            ),
            action="apiv2.object_objects_list:GET",
            initiator=request.headers.get("User-Agent"),
        )
        db.session.add(new_event)
        db.session.commit()

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
        if name_ilike:
            query = query.filter(JsonObject.name.ilike("%" + name_ilike + "%"))
        if object_organization is not None:
            query = query.filter(JsonObject.organization.has(name=object_organization))
        if object_schema is not None:
            # Schema name of the object
            query = query.filter(JsonObject.schema.has(name=object_schema))
        if object_schema_uuid is not None:
            # Schema UUID of the object
            query = query.join(Schema).filter(
                Schema.json_schema[("$id")].astext.like(
                    "%" + str(object_schema_uuid) + "%"
                )
            )
        if object_uuid is not None:
            query = query.filter(
                JsonObject.json_object[("uuid")].astext == str(object_uuid)
            )
        if object_language is not None:
            query = query.filter(
                JsonObject.json_object[("language")].astext == object_language
            )

        query = query.order_by(JsonObject.last_updated.desc())
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
        errors: List[int] = []
        for obj in object_ns.payload:

            check_submitted_object(obj)

            obj_licenses = []
            for license in obj.get("licenses", []):
                obj_license = License.query.filter(
                    License.license_id == license["license_id"]
                ).first()
                if obj_license:
                    obj_licenses.append(obj_license)
            try:
                del obj["licenses"]  # must be removed
                del obj["organization"]  # if not supplied by the client
            except Exception:
                pass

            try:
                new_object = JsonObject(
                    **obj, creator_id=current_user.id, editor_id=current_user.id
                )
                new_object.licenses = obj_licenses
                db.session.add(new_object)
                db.session.commit()
                result["data"].append(new_object)
                result["metadata"]["count"] += 1
            except (
                sqlalchemy.exc.IntegrityError,
                sqlalchemy.exc.InvalidRequestError,
            ) as e:
                logger.error("Error when creating object {}".format(object["id"]))
                print(e)
                # errors.append(object["id"])
                db.session.rollback()

        # if some objects can not created we return the HTTP code 207 (Multi-Status)
        # if all objects of the batch POST request are created we simply return 201.
        return result, 207 if errors else 201


@object_ns.route("/<int:id>")
class ObjectItem(Resource):
    """Get object details."""

    @object_ns.doc("object_get")
    @object_ns.marshal_with(object_get_id, code=200)
    def get(self, id):
        obj = JsonObject.query.filter(JsonObject.id == id).first()
        if obj:
            # Log the event
            new_event = Event(
                scope="JsonObject",
                subject=f"id={id}",
                action="apiv2.object_object_item:GET",
                initiator=request.headers.get("User-Agent"),
            )
            db.session.add(new_event)
            db.session.commit()
        return JsonObject.query.filter(JsonObject.id == id).all(), 200

    @object_ns.doc("object_patch")
    @object_ns.expect(object)
    @object_ns.marshal_with(object, code=201)
    @auth_func
    def patch(self, id):

        obj = JsonObject.query.filter(JsonObject.id == id).first()

        if obj:
            # Log the event
            new_event = Event(
                scope="JsonObject",
                subject=f"id={id}",
                action="apiv2.object_object_item:PATCH",
                initiator="{} user-id={}".format(
                    request.headers.get("User-Agent"), current_user.id
                ),
            )
            db.session.add(new_event)
            db.session.commit()

        data = {
            "org_id": obj.org_id,
            "schema_id": obj.schema_id,
            "object_id": id,
            "object_is_locked": obj.is_locked,
            "object_creator_id": obj.creator_id,
            "json_object": object_ns.payload["json_object"],
        }

        try:
            # check the submitted object
            check_submitted_object(data)
            # create a new version of the object to update
            create_new_version(obj.id)
            obj.editor_id = current_user.id
            # update the object
            obj.json_object = object_ns.payload["json_object"]
            db.session.commit()
        except Exception as e:
            raise (e)

        return obj, 201

    @auth_func
    def delete(self, id):
        obj = JsonObject.query.filter(JsonObject.id == id).first()
        if obj:
            # Log the event
            new_event = Event(
                scope="JsonObject",
                subject=f"id={id}",
                action="apiv2.object_object_item:DELETE",
                initiator="{} user-id={}".format(
                    request.headers.get("User-Agent"), current_user.id
                ),
            )
            db.session.add(new_event)
            db.session.commit()

            db.session.delete(obj)
            db.session.commit()
        return {}, 204
