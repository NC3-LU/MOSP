import json
import ast
import operator
import functools
from urllib.parse import urljoin
from flask import (
    Blueprint,
    Response,
    render_template,
    redirect,
    url_for,
    request,
    abort,
    flash,
)
from flask_login import login_required, current_user
from flask_babel import gettext
from flask_paginate import Pagination, get_page_args
from sqlalchemy import func, Boolean, Integer, desc, nullslast, or_

from mosp.bootstrap import db, application
from mosp.web.forms import SchemaForm
from mosp.models import Schema, JsonObject

schema_bp = Blueprint("schema_bp", __name__, url_prefix="/schema")
schemas_bp = Blueprint("schemas_bp", __name__, url_prefix="/schemas")


@schemas_bp.route("/", methods=["GET"])
def list_schemas():
    """Return the page which will display the list of schemas."""
    # Order by schema wich validates the most JSON objects.
    hot_schemas = (
        db.session.query(
            JsonObject.schema_id, func.count("*").label("JsonObject_count")
        )
        .group_by(JsonObject.schema_id)
        .subquery()
    )
    schemas = (
        db.session.query(Schema)
        .outerjoin(hot_schemas, (Schema.id == hot_schemas.c.schema_id))
        .order_by(nullslast(desc(hot_schemas.c.JsonObject_count)))
    )
    return render_template("schemas.html", schemas=schemas)


@schema_bp.route("/<int:schema_id>", defaults={"per_page": "20"}, methods=["GET"])
def get(per_page, schema_id=None):
    """Return the schema given in parameter with the objects validated by this
    schema. Also returns the objects validated by this schema. It is possible
    to filter the objects based on some properties of the schema.
    """
    schema = Schema.query.filter(Schema.id == schema_id).first()
    if schema is None:
        abort(404)

    if not current_user.is_authenticated:
        # Loads public objects related to the schema
        query = JsonObject.query.filter(JsonObject.schema_id == schema.id)
    else:
        # Loads all objects related to the schema
        query = JsonObject.query.filter(JsonObject.schema_id == schema.id)

    # Search on the fields of the JSONB object
    # 1. Look for the searchable properties of the current schema. Actuallay we
    # accept string, boolean and integer
    search_keys = {
        key: (
            key in schema.json_schema["required"],
            schema.json_schema["properties"][key].get("type", False),
        )
        for key in schema.json_schema.get("properties", [])
        if schema.json_schema["properties"][key].get("type", False)
        in ["string", "boolean", "integer"]
    }
    # 2. Get the query of the user
    search_key = request.args.get("search_key", "")
    search_term = request.args.get("search_term", "")
    # 3. Prepare the filter (query on a JSONB object)  based on the type of the
    # attribute
    if search_key and search_term:
        if search_keys[search_key][1] == "string":
            # string: ilike search
            query = query.filter(
                JsonObject.json_object[(search_key)].astext.ilike(
                    "%" + search_term + "%"
                )
            )
        elif search_keys[search_key][1] == "boolean":
            # boolean
            query = query.filter(
                JsonObject.json_object[(search_key)]
                .astext.cast(Boolean)
                .is_(ast.literal_eval(search_term))
            )
        elif search_keys[search_key][1] == "integer":
            # integer
            query = query.filter(
                JsonObject.json_object[(search_key)].astext.cast(Integer)
                == ast.literal_eval(search_term)
            )

    # Pagination
    page, per_page, offset = get_page_args()
    pagination = Pagination(
        page=page,
        total=query.count(),
        css_framework="bootstrap4",
        search=False,
        record_name="objects",
        per_page=per_page,
    )

    return render_template(
        "schema.html",
        schema=schema,
        objects=query.offset(offset).limit(per_page),
        pagination=pagination,
        search_keys=search_keys,
        search_key=search_key,
        search_term=search_term,
    )


@schema_bp.route("/view/<int:schema_id>", methods=["GET"])
def view(schema_id=None):
    """
    Display the JSON part of a Schema object and some related informations.
    """
    json_schema = Schema.query.filter(Schema.id == schema_id).first()
    if json_schema is None:
        abort(404)
    result = json.dumps(
        json_schema.json_schema, sort_keys=True, indent=4, separators=(",", ": ")
    )
    return render_template(
        "view_schema.html", json_schema=json_schema, json_schema_pretty=result
    )


@schema_bp.route("/def/<int:schema_id>", methods=["GET"])
@schema_bp.route("/def/<uuid:schema_uuid>", methods=["GET"])
def definition(schema_id=None, schema_uuid=None):
    """
    Returns the defintion of a JSON schema (text/plain).
    """
    schema_uuid_absolute = urljoin(
        application.config["INSTANCE_URL"], "schema/def/" + str(schema_uuid)
    )
    json_schema = Schema.query.filter(
        or_(
            Schema.id == schema_id,
            Schema.json_schema[("$id")].astext == schema_uuid_absolute,
        )
    ).first()
    if json_schema is None:
        abort(404)
    result = json.dumps(
        json_schema.json_schema, sort_keys=True, indent=4, separators=(",", ": ")
    )
    return Response(result, mimetype="text/plain")


@schema_bp.route("/<int:schema_id>/get_objects", methods=["GET"])
def get_objects(schema_id=None):
    """Returns all JSON objects (JsonObject.json_object) validated by the
    JSON schema.
    """
    json_schema = Schema.query.filter(Schema.id == schema_id).first()
    if json_schema is None:
        abort(404)
    # Get all JSON objects (JsonObject.json_object) validated by this schema
    json_objects = [
        elem.json_object if isinstance(elem.json_object, list) else [elem.json_object]
        for elem in json_schema.objects
    ]
    # Flatten the list json_objects
    flat_json_objects = functools.reduce(operator.iconcat, json_objects, [])
    # Prepare the result
    result = json.dumps(
        flat_json_objects, sort_keys=True, indent=4, separators=(",", ": ")
    )
    return Response(
        result,
        mimetype="application/json",
        headers={
            "Content-Disposition": "attachment;filename={}.json".format(
                json_schema.name.replace(" ", "_")
            )
        },
    )


@schema_bp.route("/create", methods=["GET"])
@schema_bp.route("/edit/<int:schema_id>", methods=["GET"])
@login_required
def form(schema_id=None, org_id=None):
    """Returns a form in order to edit a schema."""
    action = gettext("Create a schema")
    head_titles = [action]

    form = SchemaForm()
    form.org_id.choices = [(0, "")]
    form.org_id.choices.extend(
        [(org.id, org.name) for org in current_user.organizations]
    )

    if schema_id is None:
        # Creation of a new schema

        # initialization of the minimum for a valid JSON schema with an ID on
        # this platform.
        default_minimum_json_schema = {
            "id": "{}".format(
                urljoin(
                    application.config["INSTANCE_URL"],
                    "schema/def/<UUID-of-the-schema>",
                )
            ),
            "$schema": "http://json-schema.org/schema#",
            "title": "Title of the schema",
            "description": "Description of the purpose of this schema.",
            "type": "object",
            "properties": {},
            "required": [],
        }
        form.json_schema.data = json.dumps(
            default_minimum_json_schema,
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )
        # set the organization id
        org_id = request.args.get("org_id", None)
        if org_id is not None:
            form.org_id.data = int(org_id)
        return render_template(
            "edit_schema.html",
            action=action,
            head_titles=head_titles,
            form=form,
            schema_id=schema_id,
        )

    # Edition of an existing schema
    schema = Schema.query.filter(Schema.id == schema_id).first()
    form = SchemaForm(obj=schema)
    form.json_schema.data = json.dumps(
        schema.json_schema, sort_keys=True, indent=4, separators=(",", ": ")
    )
    form.org_id.choices = [(0, "")]
    form.org_id.choices.extend(
        [(org.id, org.name) for org in current_user.organizations]
    )
    action = gettext("Edit a schema")
    head_titles = [action]
    head_titles.append(schema.name)
    return render_template(
        "edit_schema.html",
        action=action,
        head_titles=head_titles,
        schema=schema,
        form=form,
        schema_id=schema_id,
    )


@schema_bp.route("/create", methods=["POST"])
@schema_bp.route("/edit/<int:schema_id>", methods=["POST"])
@login_required
def process_form(schema_id=None):
    """"Process the form to edit a schema."""
    form = SchemaForm()
    form.org_id.choices = [(0, "")]
    form.org_id.choices.extend(
        [(org.id, org.name) for org in current_user.organizations]
    )

    if not form.validate():
        if form.org_id.data == 0:
            flash(gettext("You must specify an organization."), "warning")
        return redirect(url_for("schema_bp.form"))

    # Edit an existing schema
    if schema_id is not None:
        schema = Schema.query.filter(Schema.id == schema_id).first()
        schema_json_obj = json.loads(form.json_schema.data)
        del form.json_schema
        form.populate_obj(schema)
        schema.json_schema = schema_json_obj
        try:
            db.session.commit()
            flash(
                gettext(
                    "%(object_name)s successfully updated.", object_name=form.name.data
                ),
                "success",
            )
        except Exception:
            form.name.errors.append("Name already exists.")
        return redirect(url_for("schema_bp.form", schema_id=schema.id))

    # Create a new schema
    schema_json_obj = json.loads(form.json_schema.data)
    new_schema = Schema(
        name=form.name.data,
        description=form.description.data,
        json_schema=schema_json_obj,
        org_id=form.org_id.data,
        creator_id=current_user.id,
    )
    db.session.add(new_schema)
    try:
        db.session.commit()
        flash(
            gettext(
                "%(object_name)s successfully created.", object_name=new_schema.name
            ),
            "success",
        )
    except Exception:
        return redirect(url_for("schema_bp.form"))
    return redirect(url_for("schema_bp.form", schema_id=new_schema.id))


@schema_bp.route("/delete/<int:schema_id>", methods=["GET"])
@login_required
def delete(schema_id=None):
    """
    Delete the requested schema.
    """
    schema = Schema.query.filter(Schema.id == schema_id).first()
    db.session.delete(schema)
    db.session.commit()
    return redirect(url_for("schemas_bp.list_schemas"))
