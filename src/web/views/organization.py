from flask import Blueprint, render_template, abort
from flask_paginate import Pagination, get_page_args
from sqlalchemy import or_

from web.models import Organization, JsonObject, Schema

organization_bp = Blueprint('organization_bp', __name__, url_prefix='/organization')
organizations_bp = Blueprint('organizations_bp', __name__, url_prefix='/organizations')


@organizations_bp.route('/', methods=['GET'])
def list_organizations():
    """Return the page which will display the list of organizations."""
    return render_template('organizations.html')


@organization_bp.route('/<int:organization_id>', defaults={'per_page_objects': '10', 'per_page_schemas': '10'}, methods=['GET'])
@organization_bp.route('/<string:organization_name>', defaults={'per_page_objects': '10', 'per_page_schemas': '10'}, methods=['GET'])
def get(per_page_objects, per_page_schemas, organization_id=None, organization_name=None):
    """Return the organization given in parameter."""
    org = Organization.query.filter(or_(Organization.id == organization_id,
            Organization.name == organization_name)).first()
    if org is None:
        abort(404)
    # Pagination on objects created by the organization
    query_objects = JsonObject.query.filter(JsonObject.org_id==org.id)
    page_objects, per_page_objects, offset = get_page_args()
    pagination_objects = Pagination(page_parameter='page_objects',
                            per_page_parameter='per_page_objects',
                            page=page_objects, total=query_objects.count(),
                            css_framework='bootstrap4',
                            search=False, record_name='objects',
                            per_page=per_page_objects)
     # Pagination on objects created by the organization
    query_schemas = Schema.query.filter(Schema.org_id==org.id)
    page_schemas, per_page_schemas, offset = get_page_args()
    pagination_schemas = Pagination(page_parameter='page_schemas',
                            per_page_parameter='per_page_schemas',
                            page=page_schemas, total=query_schemas.count(),
                            css_framework='bootstrap4',
                            search=False, record_name='schemas',
                            per_page=per_page_schemas)
    return render_template('organization.html', organization=org,
                           pagination_objects=pagination_objects,
                           pagination_schemas=pagination_schemas,
                           objects=query_objects.offset(offset).limit(per_page_objects),
                           schemas=query_schemas.offset(offset).limit(per_page_schemas))
