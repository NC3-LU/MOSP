import json
from flask import Blueprint, render_template, redirect, url_for, flash, \
                    request, abort
from flask_login import login_required, current_user
from flask_babel import gettext
from sqlalchemy import or_, func

from bootstrap import db
from web.forms import SchemaForm
from web.models import Schema, JsonObject, Organization

schema_bp = Blueprint('schema_bp', __name__, url_prefix='/schema')
schemas_bp = Blueprint('schemas_bp', __name__, url_prefix='/schemas')


@schemas_bp.route('/', methods=['GET'])
def list_schemas():
    """Return the page which will display the list of schemas."""
    #schemas = db.session.query(Schema, func.count(Schema.objects).label('total')).order_by('total DESC')
    #schemas = db.session.query(Schema, func.count(JsonObject.id).label('total')).join(JsonObject).group_by(Schema).order_by('total DESC')
    #print(schemas.first())
    schemas = Schema.query.filter().all()
    return render_template('schemas.html', schemas=schemas)


@schema_bp.route('/<int:schema_id>', methods=['GET'])
def get(schema_id=None):
    """Return the schema given in parameter with the objects validated by this
    schema."""
    schema = Schema.query.filter(Schema.id == schema_id).first()
    if schema is None:
        abort(404)
    if not current_user.is_authenticated:
        # Loads public objects related to the schema
        objects = JsonObject.query. \
                filter(JsonObject.schema_id==schema.id). \
                filter(JsonObject.is_public)
    elif current_user.is_admin:
        # Loads all objects related to the schema
        objects = JsonObject.query.filter(JsonObject.schema_id==schema.id)
    else:
        # Loads objects related to the schema that are:
        #   - public;
        #   - private but related to the organizations the current user is
        #     affiliated to.
        objects = JsonObject.query. \
                filter(JsonObject.schema_id==schema.id). \
                filter(or_(JsonObject.is_public,
                            JsonObject.organization. \
                                has(Organization.id.in_([org.id for org in current_user.organizations]))))
    return render_template('schema.html', schema=schema, objects=objects)


@schema_bp.route('/view/<int:schema_id>', methods=['GET'])
def view(schema_id=None):
    """
    Display the JSON part of a Schema object and some related informations.
    """
    json_schema = Schema.query.filter(Schema.id == schema_id).first()
    if json_schema is None:
        abort(404)
    result = json.dumps(json_schema.json_schema,
                        sort_keys=True, indent=4, separators=(',', ': '))
    return render_template('view_schema.html',
                            json_schema=json_schema,
                            json_schema_pretty=result)


@schema_bp.route('/create', methods=['GET'])
@schema_bp.route('/edit/<int:schema_id>', methods=['GET'])
@login_required
def form(schema_id=None, org_id=None):
    action = "Create a schema"
    head_titles = [action]

    form = SchemaForm()
    form.org_id.choices = [(0, '')]
    form.org_id.choices.extend([(org.id, org.name) for org in
                                                    current_user.organizations])

    if schema_id is None:
        org_id = request.args.get('org_id', None)
        if org_id is not None:
            form.org_id.data = int(org_id)
        return render_template('edit_schema.html', action=action,
                               head_titles=head_titles, form=form)

    schema = Schema.query.filter(Schema.id == schema_id).first()
    form = SchemaForm(obj=schema)
    form.json_schema.data = json.dumps(schema.json_schema)
    form.org_id.choices = [(0, '')]
    form.org_id.choices.extend([(org.id, org.name) for org in
                                                    current_user.organizations])
    action = "Edit a schema"
    head_titles = [action]
    head_titles.append(schema.name)
    return render_template('edit_schema.html', action=action,
                           head_titles=head_titles, schema=schema, form=form)


@schema_bp.route('/create', methods=['POST'])
@schema_bp.route('/edit/<int:schema_id>', methods=['POST'])
@login_required
def process_form(schema_id=None):
    form = SchemaForm()
    form.org_id.choices = [(0, '')]
    form.org_id.choices.extend([(org.id, org.name) for org in
                                                    current_user.organizations])

    if not form.validate():
        return render_template('edit_schema.html', form=form)

    # Edit an existing schema
    if schema_id is not None:
        schema = Schema.query.filter(Schema.id == schema_id).first()
        schema_json_obj = json.loads(form.json_schema.data)
        del form.json_schema
        form.populate_obj(schema)
        schema.json_schema = schema_json_obj
        try:
            db.session.commit()
            flash(gettext('%(object_name)s successfully updated.',
                    object_name=form.name.data), 'success')
        except Exception as e:
            form.name.errors.append('Name already exists.')
        return redirect(url_for('schema_bp.form', schema_id=schema.id))

    # Create a new schema
    schema_json_obj = json.loads(form.json_schema.data)
    new_schema = Schema(name=form.name.data,
                        description=form.description.data,
                        json_schema=schema_json_obj,
                        org_id=form.org_id.data,
                        creator_id=current_user.id)
    db.session.add(new_schema)
    try:
        db.session.commit()
        flash(gettext('%(object_name)s successfully created.',
                object_name=new_schema.name), 'success')
    except Exception as e:
        # TODO: display the error
        return redirect(url_for('schema_bp.form', schema_id=new_schema.id))
    return redirect(url_for('schema_bp.form', schema_id=new_schema.id))


@schema_bp.route('/delete/<int:schema_id>', methods=['GET'])
@login_required
def delete(schema_id=None):
    """
    Delete the requested schema.
    """
    schema = Schema.query.filter(Schema.id == schema_id).first()
    db.session.delete(schema)
    db.session.commit()
    return redirect(url_for('schemas_bp.list_schemas'))
