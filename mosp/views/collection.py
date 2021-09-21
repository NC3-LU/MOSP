from flask import Blueprint, render_template, abort
from flask_login import login_required
from flask_babel import gettext

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

    return head_titles
