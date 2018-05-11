from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import or_

from bootstrap import db
from web.models import Schema, JsonObject, User, Organization

schema_bp = Blueprint('schema_bp', __name__, url_prefix='/schema')
schemas_bp = Blueprint('schemas_bp', __name__, url_prefix='/schemas')


@schemas_bp.route('/', methods=['GET'])
def list_shemas():
    """Return the page which will display the list of schemas."""
    return render_template('schemas.html')


@schema_bp.route('/<int:schema_id>', methods=['GET'])
def get(schema_id=None):
    """Return the schema given in parameter with the objects validated by this
    schema."""
    schema = Schema.query.filter(Schema.id == schema_id).first()
    if schema is None:
        abort(404)
    if not current_user.is_authenticated:
        objects = JsonObject.query. \
                filter(JsonObject.schema_id==schema.id). \
                filter(JsonObject.is_public)
    elif current_user.is_admin:
        # Loads all objects related to the schema
        objects = JsonObject.query.filter(JsonObject.schema_id==schema.id)
    else:
        # Loads objects related to the schema which are:
        #   - public;
        #   - private but related to the organizations the current user is
        #     affiliated to.
        objects = JsonObject.query. \
                filter(JsonObject.schema_id==schema.id). \
                filter(or_(JsonObject.is_public,
                            JsonObject.organization. \
                                has(Organization.id.in_([org.id for org in current_user.organizations]))))
    return render_template('schema.html', schema=schema, objects=objects)
