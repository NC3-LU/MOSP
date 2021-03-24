#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Resources shared between all APIs.
"""

import jsonschema
from flask_login import current_user
from flask_restless import ProcessingException

from mosp.models import Schema, Organization


def check_submitted_object(data):
    """Ensures. a user has the rights to create/edit an abject
    in a specific organization.
    Checks also the validity of the submitted JSON object against the specified
    the JSON schema.
    """
    schema_id = data.get("schema_id", None)
    org_id = data.get("org_id", None)

    if org_id is None:
        raise ProcessingException(
            description="You must provide the id of an organization.", code=400
        )
    if org_id not in [org.id for org in current_user.organizations] + list(
        next(
            zip(
                *Organization.query.filter(
                    Organization.is_membership_restricted == False
                )
                .with_entities(Organization.id)
                .all()
            )
        )
    ):
        raise ProcessingException(
            description="You are not allowed to create/edit object in this organization.",
            code=400,
        )

    if schema_id is None:
        raise ProcessingException(
            description="You must provide the id of a schema.", code=400
        )
    schema = Schema.query.filter(Schema.id == schema_id)
    if not schema.count():
        raise ProcessingException(description="Bad schema id", code=400)
    try:
        # check the validity of the submitted object
        # (note: an empty JSON object is validated by any schema)
        jsonschema.validate(data.get("json_object", {}), schema.first().json_schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ProcessingException(
            description="The object submited is not validated by the schema:\n{}".format(
                e.message
            ),
            code=400,
        )
    except Exception:
        raise ProcessingException(description="Unknown error.", code=400)
