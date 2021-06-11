import json
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    Response,
    jsonify,
)
from flask_login import login_required, current_user
from flask_babel import gettext

from mosp.bootstrap import db
from mosp.models import Schema, JsonObject, License
from mosp.views.decorators import check_object_edit_permission
from mosp.forms import AddObjectForm
from mosp.lib import objects_utils

object_bp = Blueprint("object_bp", __name__, url_prefix="/object")
objects_bp = Blueprint("objects_bp", __name__, url_prefix="/objects")


@object_bp.route("/<uuid:object_uuid>", methods=["GET"])
def get_by_uuid(object_uuid):
    """
    Export the JSON part of a JsonObject as a clean JSON file.
    """
    query = JsonObject.query.filter(
        JsonObject.json_object[("uuid")].astext == str(object_uuid)
    )
    if not query.count():
        abort(404)
    if query.count() == 1:
        json_object = query.first()
        result = json.dumps(
            json_object.json_object, sort_keys=True, indent=4, separators=(",", ": ")
        )
        return redirect(url_for("object_bp.view", object_id=json_object.id))
    else:
        return render_template(
            "list_objects.html", uuid=object_uuid, objects=query.all()
        )


@object_bp.route("/get/<int:object_id>", methods=["GET"])
def get_json_object(object_id):
    """
    Export the JSON part of a JsonObject as a clean JSON file.
    """
    json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
    if json_object is None:
        abort(404)
    result = json.dumps(
        json_object.json_object, sort_keys=True, indent=4, separators=(",", ": ")
    )
    return Response(
        result,
        mimetype="application/json",
        headers={
            "Content-Disposition": "attachment;filename={}.json".format(
                json_object.name.replace(" ", "_")
            )
        },
    )


@object_bp.route("/galaxy/<int:object_id>", methods=["GET"])
def get_misp_galaxy_cluster(object_id):
    """Return the MISP galaxy and cluster from the object."""
    json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
    if json_object is None:
        abort(404)
    galaxy, cluster = objects_utils.generate_misp_galaxy_cluster(json_object)
    tar_file = objects_utils.generate_tar_gz_archive(galaxy, cluster)

    return Response(
        tar_file,
        mimetype="application/x-tar",
        headers={
            "Content-Disposition": "attachment;filename={}.tgz".format(
                json_object.name.replace(" ", "_")
            )
        },
    )


@object_bp.route("/view/<int:object_id>", methods=["GET"])
def view(object_id=None):
    """
    Display the JSON part of a JsonObject object and some related informations.
    """
    # res = JsonObject.query.filter(JsonObject.json_object.contains(
    #                     {'predicates': [{'value': 'source-type'}]}
    #                     )).all()
    # res = JsonObject.query.filter(JsonObject.json_object.contains(
    #                     {'values': [{'entry': [{'value': 'news-report'}]}]}
    #                     )).all()
    # res = JsonObject.query.filter(JsonObject.json_object[('namespace')].astext == 'osint')
    # res = JsonObject.query.filter(JsonObject.json_object[('father-uuid')].astext == 'fdsfsf')
    # res = JsonObject.query.filter(JsonObject.json_object[('mapping', 'father-uuid')].astext == 'fdsfsf')
    # res = JsonObject.query.filter(JsonObject.json_object[('mapping'), [('father-uuid')]].astext == "fdsfsf")
    json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
    if json_object is None:
        abort(404)
    try:
        uuid = json_object.json_object["uuid"]
    except Exception:
        uuid = None
    result = json.dumps(
        json_object.json_object,
        ensure_ascii=False,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    )
    return render_template(
        "view_object.html",
        uuid=uuid,
        json_object=json_object,
        json_object_pretty=result,
    )


@object_bp.route("/delete/<int:object_id>", methods=["GET"])
@login_required
@check_object_edit_permission
def delete(object_id=None):
    """
    Delete the requested JsonObject.
    """
    json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
    schema_id = json_object.schema_id
    db.session.delete(json_object)
    db.session.commit()
    return redirect(url_for("schema_bp.get", schema_id=schema_id))


@object_bp.route("/jsoneditor/<int:object_id>", methods=["GET"])
@login_required
@check_object_edit_permission
def edit_json(object_id=None):
    """
    Edit a JSON object with JSON editor.
    """
    action = "Edit an object"
    head_titles = [action]
    json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
    schema = json_object.schema

    try:
        duplicates = objects_utils.check_duplicates(json_object)
        flash(
            'An object with the same UUID exists: <a href="{}" target="_blank">{}</a>'.format(
                url_for("object_bp.view", object_id=duplicates[0].id),
                duplicates[0].name,
            ),
            "warning",
        )
    except Exception:
        pass

    return render_template(
        "edit_json.html",
        action=action,
        head_titles=head_titles,
        schema=schema,
        json_object=json_object,
    )


@object_bp.route("/create", methods=["GET"])
@object_bp.route("/edit/<int:object_id>", methods=["GET"])
@login_required
@check_object_edit_permission
def form(schema_id=None, object_id=None):
    action = "Create an object"
    head_titles = [action]

    form = AddObjectForm()
    form.org_id.choices = [(0, "")]
    form.org_id.choices.extend(
        [(org.id, org.name) for org in current_user.organizations]
    )

    if object_id is None:
        schema_id = request.args.get("schema_id", None)
        form.schema_id.data = schema_id
        schema = Schema.query.filter(Schema.id == schema_id).first()
        return render_template(
            "edit_object.html",
            action=action,
            head_titles=head_titles,
            form=form,
            schema=schema,
        )

    json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
    schema = json_object.schema
    form = AddObjectForm(obj=json_object)
    form.schema_id.data = schema.id
    form.org_id.choices = [(0, "")]
    form.org_id.choices.extend(
        [(org.id, org.name) for org in current_user.organizations]
    )
    form.licenses.data = [license.id for license in json_object.licenses]
    form.refers_to.data = [
        jsonobject.id
        for jsonobject in json_object.refers_to
        if jsonobject.id != json_object.id
    ]
    form.refers_to.choices = [
        (jsonobject.id, jsonobject.name)
        for jsonobject in JsonObject.query.all()
        if jsonobject.id != json_object.id
    ]
    form.referred_to_by.data = [
        jsonobject.id
        for jsonobject in json_object.referred_to_by
        if jsonobject.id != json_object.id
    ]
    form.referred_to_by.choices = [
        (jsonobject.id, jsonobject.name)
        for jsonobject in JsonObject.query.all()
        if jsonobject.id != json_object.id
    ]
    action = "Edit an object"
    head_titles = [action]
    head_titles.append(json_object.name)
    return render_template(
        "edit_object.html",
        action=action,
        head_titles=head_titles,
        object_id=object_id,
        form=form,
        schema=schema,
    )


@object_bp.route("/create", methods=["POST"])
@object_bp.route("/edit/<int:object_id>", methods=["POST"])
@login_required
@check_object_edit_permission
def process_form(object_id=None):
    """"Process the form to edit an object."""
    form = AddObjectForm()
    form.org_id.choices = [(0, "")]
    form.org_id.choices.extend(
        [(org.id, org.name) for org in current_user.organizations]
    )

    if not form.validate():
        return render_template("edit_object.html", form=form)

    # Edit an existing JsonObject
    if object_id is not None:
        # Load the object to edit and create a new Version instance for the versioning.
        json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
        new_version = json_object.create_new_version()

        form.schema_id.data = json_object.schema_id
        # Licenses
        new_licenses = []
        for license_id in form.licenses.data:
            license = License.query.filter(License.id == license_id).first()
            new_licenses.append(license)
        json_object.licenses = new_licenses
        del form.licenses

        # refers_to relationship
        new_json_objects_to_link = []
        for cur_json_object_id in form.refers_to.data:
            json_object_dep = JsonObject.query.filter(
                JsonObject.id == cur_json_object_id
            ).first()
            new_json_objects_to_link.append(json_object_dep)
        json_object.refers_to = new_json_objects_to_link
        del form.refers_to

        # referred_to_by relationship
        new_json_objects_to_link = []
        for cur_json_object_id in form.referred_to_by.data:
            json_object_dep = JsonObject.query.filter(
                JsonObject.id == cur_json_object_id
            ).first()
            new_json_objects_to_link.append(json_object_dep)
        json_object.referred_to_by = new_json_objects_to_link
        del form.referred_to_by

        form.populate_obj(json_object)
        try:
            db.session.commit()
            flash(
                gettext(
                    "%(object_name)s successfully updated.", object_name=form.name.data
                ),
                "success",
            )
        except Exception as e:
            print(e)
            form.name.errors.append("Name already exists.")
        return redirect(url_for("object_bp.form", object_id=json_object.id))

    # Create a new JsonObject
    new_object = JsonObject(
        name=form.name.data,
        description=form.description.data,
        schema_id=form.schema_id.data,
        org_id=form.org_id.data,
        creator_id=current_user.id,
    )
    db.session.add(new_object)
    try:
        db.session.commit()
    except Exception:
        return redirect(url_for("object_bp.form", object_id=new_object.id))

    # Licenses
    new_licenses = []
    for license_id in form.licenses.data:
        license = License.query.filter(License.id == license_id).first()
        new_licenses.append(license)
    new_object.licenses = new_licenses
    del form.licenses

    # refers_to relationship
    new_json_objects_to_link = []
    for cur_json_object_id in form.refers_to.data:
        json_object_dep = JsonObject.query.filter(
            JsonObject.id == cur_json_object_id
        ).first()
        new_json_objects_to_link.append(json_object_dep)
    new_object.refers_to = new_json_objects_to_link
    del form.refers_to

    # referred_to_by relationship
    new_json_objects_to_link = []
    for cur_json_object_id in form.referred_to_by.data:
        json_object_dep = JsonObject.query.filter(
            JsonObject.id == cur_json_object_id
        ).first()
        new_json_objects_to_link.append(json_object_dep)
    new_object.referred_to_by = new_json_objects_to_link
    del form.referred_to_by

    try:
        db.session.commit()
        flash(
            gettext(
                "%(object_name)s successfully created.", object_name=new_object.name
            ),
            "success",
        )
    except Exception:
        return redirect(url_for("object_bp.form", object_id=new_object.id))

    return redirect(url_for("object_bp.form", object_id=new_object.id))


@object_bp.route("/copy/<int:object_id>", methods=["GET"])
@login_required
@check_object_edit_permission
def copy(object_id=None):
    """Copy an object from one organization to another."""
    org_id = request.args.get("org_id", None)
    if org_id is None:
        abort(404)
    if int(org_id) not in [org.id for org in current_user.organizations]:
        abort(404)

    json_object = JsonObject.query.filter(JsonObject.id == object_id).first()
    if json_object is None:
        abort(404)

    new_object = JsonObject()
    new_object.org_id = org_id
    new_object.schema_id = json_object.schema_id
    new_object.creator_id = current_user.id
    new_object.licenses = json_object.licenses
    new_object.name = json_object.name
    new_object.description = json_object.description
    new_object.json_object = json_object.json_object
    new_object.refers_to.append(json_object)
    new_object.last_updated = datetime.utcnow()

    db.session.add(new_object)
    db.session.commit()

    return jsonify(id=new_object.id)
