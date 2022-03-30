#! /usr/bin/env python
"""
Resources shared between all APIs.
"""
import jsonschema
from flask_login import current_user
from flask_restx import abort

from mosp.models import JsonObject
from mosp.models import Organization
from mosp.models import Schema


def check_submitted_object(data):
    """Ensures a user has the rights to create/edit an object
    in a specific organization.
    Checks also the validity of the submitted JSON object against the specified
    the JSON schema.
    """
    schema_id = data.get("schema_id", None)
    org_id = data.get("org_id", None)
    object_id = data.get("object_id", None)

    # check if the user has rights in the corresponding organization.
    if org_id is None:
        raise abort(400, description="You must provide the id of an organization.")

    try:
        open_orgs = list(
            next(
                zip(
                    *Organization.query.filter(
                        Organization.is_membership_restricted == False  # noqa
                    )
                    .with_entities(Organization.id)
                    .all()
                )
            )
        )
    except StopIteration:
        open_orgs = []

    if org_id not in [org.id for org in current_user.organizations] + open_orgs:
        raise abort(
            400,
            description="You are not allowed to create/edit an object in this organization.",
        )

    # check if the object is locked: only its creator can edit it.
    if (
        object_id  # only in case of edition of an existing object
        and data.get("object_is_locked", True)
        and data.get("object_creator_id", 0) != current_user.id
    ):
        raise abort(
            400,
            description="You are not allowed to edit this locked object.",
        )

    # check if the object is validated by the JSON schema
    if schema_id is None:
        raise abort(400, description="You must provide the id of a schema.")
    schema = Schema.query.filter(Schema.id == schema_id)
    if not schema.count():
        raise abort(400, description="Bad schema id")
    try:
        # check the validity of the submitted object
        # (note: an empty JSON object is validated by any schema)
        jsonschema.validate(data.get("json_object", {}), schema.first().json_schema)
    except jsonschema.exceptions.ValidationError as e:
        raise abort(
            400,
            description="The object submited is not validated by the schema:\n{}".format(
                e.message
            ),
        )
    except jsonschema.exceptions.SchemaError as e:
        raise abort(
            400,
            description=f"Schema error:\n{e.message}",
        )
    except Exception:
        raise abort(400, description="Unknown error.")


def create_new_version(object_id):
    """Create a new version of the object to update."""
    json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
    json_object.create_new_version()
    json_object.editor_id = current_user.id
