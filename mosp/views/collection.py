from flask import Blueprint, render_template, abort

from mosp.models import Collection

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
