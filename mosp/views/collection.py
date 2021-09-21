from flask import Blueprint, render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_babel import gettext

from mosp.bootstrap import db
from mosp.models import Collection
from mosp.forms import CollectionForm

collection_bp = Blueprint("collection_bp", __name__, url_prefix="/collection")
collections_bp = Blueprint("collections_bp", __name__, url_prefix="/collections")


@collections_bp.route("/", methods=["GET"])
def list_collections():
    """Return the page which will display the list of collections."""
    collections = Collection.query.all()
    return render_template("collections.html", collections=collections)


@collection_bp.route(
    "/<int:collection_id>",
    defaults={"per_page": "10"},
    methods=["GET"],
)
def get(collection_id=None):
    """Return details about the collection."""
    elem = Collection.query.filter(Collection.id == collection_id).first()
    if elem is None:
        abort(404)

    return render_template(
        "collection.html",
        collection=elem,
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
            collection_id=collection_id,
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
        collection_id=collection_id,
    )


@collection_bp.route("/create", methods=["POST"])
@collection_bp.route("/edit/<int:collection_id>", methods=["POST"])
@login_required
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
