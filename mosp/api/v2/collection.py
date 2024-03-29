#! /usr/bin/env python
from flask_restx import fields
from flask_restx import Namespace
from flask_restx import reqparse
from flask_restx import Resource

from mosp.api.v2.common import collection_params_model
from mosp.api.v2.common import metada_params_model
from mosp.api.v2.types import ResultType
from mosp.models import Collection


collection_ns = Namespace("collection", description="collection related operations")


# Argument Parsing
parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="The name of the object.")
parser.add_argument(
    "name_ilike", required=False, type=str, help="Part of the name of the object."
)
parser.add_argument("page", type=int, required=False, default=1, help="Page number")
parser.add_argument("per_page", type=int, required=False, default=10, help="Page size")


# Response marshalling
object = collection_ns.model("Collection", collection_params_model)
metadata = collection_ns.model("metadata", metada_params_model)
collection_list_fields = collection_ns.model(
    "CollectionsList",
    {
        "metadata": fields.Nested(
            metadata, description="Metada related to the result."
        ),
        "data": fields.List(fields.Nested(object), description="List of collections."),
    },
)


@collection_ns.route("/")
class CollectionsList(Resource):
    """List all collections."""

    @collection_ns.doc("list_collections")
    @collection_ns.expect(parser)
    @collection_ns.marshal_list_with(collection_list_fields)
    def get(self):
        """List all collections."""

        args = parser.parse_args()
        offset = args.pop("page", 1) - 1
        limit = args.pop("per_page", 10)
        name_ilike = args.pop("name_ilike")
        args = {k: v for k, v in args.items() if v is not None}

        result: ResultType = {
            "data": [],
            "metadata": {
                "count": 0,
                "offset": offset,
                "limit": limit,
            },
        }

        try:
            query = Collection.query
            for arg in args:
                if hasattr(Collection, arg):
                    query = query.filter(getattr(Collection, arg) == args[arg])

            if name_ilike:
                query = query.filter(Collection.name.ilike("%" + name_ilike + "%"))

            total = query.count()
            query = query.limit(limit)
            results = query.offset(offset * limit)
            count = total
        except Exception as e:
            print(e)

        result["data"] = results
        result["metadata"]["count"] = count

        return result, 200
