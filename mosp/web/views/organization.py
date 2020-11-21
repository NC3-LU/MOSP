from flask import Blueprint, render_template, abort
from flask_paginate import Pagination, get_page_args
from sqlalchemy import func, desc, nullslast, or_

from mosp.bootstrap import db
from mosp.models import Organization, JsonObject, Schema

organization_bp = Blueprint("organization_bp", __name__, url_prefix="/organization")
organizations_bp = Blueprint("organizations_bp", __name__, url_prefix="/organizations")


@organizations_bp.route("/", methods=["GET"])
def list_organizations():
    """Return the page which will display the list of organizations."""
    # Order by organization wich provides the most JSON objects.
    big_contributors = (
        db.session.query(JsonObject.org_id, func.count("*").label("JsonObject_count"))
        .group_by(JsonObject.org_id)
        .subquery()
    )
    organizations = (
        db.session.query(Organization)
        .outerjoin(big_contributors, (Organization.id == big_contributors.c.org_id))
        .order_by(nullslast(desc(big_contributors.c.JsonObject_count)))
    )
    return render_template("organizations.html", organizations=organizations)


@organization_bp.route(
    "/<int:organization_id>",
    defaults={"per_page_objects": "10", "per_page_schemas": "10"},
    methods=["GET"],
)
@organization_bp.route(
    "/<string:organization_name>",
    defaults={"per_page_objects": "10", "per_page_schemas": "10"},
    methods=["GET"],
)
def get(
    per_page_objects, per_page_schemas, organization_id=None, organization_name=None
):
    """Return details about the organization."""
    org = Organization.query.filter(
        or_(Organization.id == organization_id, Organization.name == organization_name)
    ).first()
    if org is None:
        abort(404)

    # Pagination on objects created by the organization
    query_objects = JsonObject.query.filter(JsonObject.org_id == org.id)
    page_objects, per_page_objects, offset_objects = get_page_args(
        page_parameter="page_objects", per_page_parameter="per_page_objects"
    )
    pagination_objects = Pagination(
        page_parameter="page_objects",
        page=page_objects,
        per_page=per_page_objects,
        total=query_objects.count(),
        css_framework="bootstrap4",
        search=False,
    )
    # Pagination on schemas created by the organization
    query_schemas = Schema.query.filter(Schema.org_id == org.id)
    page_schemas, per_page_schemas, offset_schemas = get_page_args(
        page_parameter="page_schemas", per_page_parameter="per_page_schemas"
    )
    pagination_schemas = Pagination(
        page_parameter="page_schemas",
        page=page_schemas,
        per_page=per_page_schemas,
        total=query_schemas.count(),
        css_framework="bootstrap4",
        search=False,
    )

    return render_template(
        "organization.html",
        organization=org,
        pagination_objects=pagination_objects,
        pagination_schemas=pagination_schemas,
        objects=query_objects.offset(offset_objects).limit(per_page_objects),
        schemas=query_schemas.offset(offset_schemas).limit(per_page_schemas),
    )
