from flask import Blueprint, render_template, abort, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_args
from flask_babel import gettext
from sqlalchemy import or_

from mosp.bootstrap import db
from mosp.models import Collection, JsonObject, User
from mosp.forms import CollectionForm
from mosp.views.decorators import check_collection_edit_permission

collection_bp = Blueprint("collection_bp", __name__, url_prefix="/collection")
collections_bp = Blueprint("collections_bp", __name__, url_prefix="/collections")


@collections_bp.route("/", methods=["GET"])
def list_collections():
    """Return the page which will display the list of collections."""
    collections = Collection.query.order_by(Collection.last_updated.desc()).all()
    return render_template("collections.html", collections=collections)


@collection_bp.route(
    "/<int:collection_id>", defaults={"per_page": "15"}, methods=["GET"]
)
@collection_bp.route(
    "/<uuid:collection_uuid>", defaults={"per_page": "15"}, methods=["GET"]
)
def get(per_page, collection_id=None, collection_uuid=None):
    """Return details about the collection."""
    elem = Collection.query.filter(
        or_(Collection.id == collection_id, Collection.uuid == collection_uuid)
    ).first()
    if elem is None:
        abort(404)

    creator = User.query.filter(User.id == elem.creator_id).first()

    # Pagination
    page, per_page, offset = get_page_args()
    pagination = Pagination(
        page=page,
        total=len(elem.objects),
        css_framework="bootstrap4",
        search=False,
        record_name="objects",
        per_page=per_page,
    )

    return render_template(
        "collection.html",
        collection=elem,
        objects=elem.objects[offset:][:per_page],
        creator=creator,
        pagination=pagination,
    )


@collection_bp.route("/create", methods=["GET"])
@collection_bp.route("/edit/<int:collection_id>", methods=["GET"])
@login_required
def form(collection_id=None):
    """Returns a form in order to edit a collection."""
    action = gettext("Create a collection")
    head_titles = [action]

    form = CollectionForm()

    if collection_id is None:
        # Creation of a new collection
        return render_template(
            "edit_collection.html",
            action=action,
            head_titles=head_titles,
            form=form,
            collection=None,
        )

    # Edition of an existing collection
    collection = Collection.query.filter(Collection.id == collection_id).first()
    form = CollectionForm(obj=collection)
    action = gettext("Edit a collection")
    head_titles = [action]
    head_titles.append(collection.name)

    return render_template(
        "edit_collection.html",
        action=action,
        head_titles=head_titles,
        form=form,
        collection=collection,
    )


@collection_bp.route("/create", methods=["POST"])
@collection_bp.route("/edit/<int:collection_id>", methods=["POST"])
@login_required
@check_collection_edit_permission
def process_form(collection_id=None):
    """ "Process the form to edit a collection."""
    form = CollectionForm()

    if collection_id is not None:
        collection = Collection.query.filter(Collection.id == collection_id).first()
        form.populate_obj(collection)

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
        return redirect(url_for("collection_bp.form", collection_id=collection.id))

    # Create a new collection
    new_collection = Collection(
        name=form.name.data,
        description=form.description.data,
        creator_id=current_user.id,
    )
    db.session.add(new_collection)
    try:
        db.session.commit()
        flash(
            gettext(
                "%(object_name)s successfully created.", object_name=new_collection.name
            ),
            "success",
        )
    except Exception:
        return redirect(url_for("collection_bp.form"))
    return redirect(url_for("collection_bp.form", collection_id=new_collection.id))


@collection_bp.route(
    "/add_to_collection/<int:collection_id>/<string:objects_id>", methods=["GET"]
)
@login_required
@check_collection_edit_permission
def add_to_collection(collection_id=None, objects_id=None):
    """Add one or several object(s) to a collection."""
    added_objects = []
    elem = Collection.query.filter(Collection.id == collection_id).first()
    for object_id in objects_id.split(","):
        obj = JsonObject.query.filter(JsonObject.id == object_id).first()
        if obj not in elem.objects:
            elem.objects.append(obj)
            try:
                db.session.commit()
                added_objects.append((obj.id, obj.name))
            except Exception:
                continue
    return jsonify(
        result="OK",
        data=added_objects,
    )


@collection_bp.route(
    "/remove_from_collection/<int:collection_id>/<int:object_id>", methods=["GET"]
)
@login_required
@check_collection_edit_permission
def remove_from_collection(collection_id=None, object_id=None):
    """Remove an object from a collection."""
    elem = Collection.query.filter(Collection.id == collection_id).first()
    obj = JsonObject.query.filter(JsonObject.id == object_id).first()
    elem.objects.remove(obj)
    db.session.commit()
    return redirect(url_for("collection_bp.form", collection_id=elem.id))


@collection_bp.route("/delete/<int:collection_id>", methods=["GET"])
@login_required
@check_collection_edit_permission
def delete(collection_id=None):
    """
    Delete the requested collection.
    """
    elem = Collection.query.filter(Collection.id == collection_id).first()
    if elem:
        db.session.delete(elem)
        db.session.commit()
        flash(
            gettext("%(object_name)s successfully deleted.", object_name=elem.name),
            "success",
        )
    return redirect(url_for("collections_bp.list_collections"))
