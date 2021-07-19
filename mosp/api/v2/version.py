#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restx import Namespace, Resource, fields, reqparse

from mosp.models import Version
from mosp.api.v2.common import version_params_model, metada_params_model


version_ns = Namespace(
    "version", description="version related operations"
)


# Argument Parsing
parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="The name of the object.")
parser.add_argument("page", type=int, required=False, default=1, help="Page number")
parser.add_argument("per_page", type=int, required=False, default=10, help="Page size")


# Response marshalling
object = version_ns.model("Version", version_params_model)
metadata = version_ns.model("metadata", metada_params_model)
version_list_fields = version_ns.model(
    "VersionsList",
    {
        "metadata": fields.Nested(
            metadata, description="Metada related to the result."
        ),
        "data": fields.List(
            fields.Nested(object), description="List of versions."
        ),
    },
)


@version_ns.route("/")
class VersionsList(Resource):
    """List all versions."""

    @version_ns.doc("list_versions")
    @version_ns.expect(parser)
    @version_ns.marshal_list_with(version_list_fields)
    def get(self):
        """List all versions."""

        args = parser.parse_args()
        offset = args.pop("page", 1) - 1
        limit = args.pop("per_page", 10)
        args = {k: v for k, v in args.items() if v is not None}

        result = {
            "data": [],
            "metadata": {
                "count": 0,
                "offset": offset,
                "limit": limit,
            },
        }

        try:
            query = Version.query
            for arg in args:
                if hasattr(Version, arg):
                    query = query.filter(getattr(Version, arg) == args[arg])
            total = query.count()
            query = query.limit(limit)
            results = query.offset(offset * limit)
            count = total
        except Exception as e:
            print(e)

        result["data"] = results
        result["metadata"]["count"] = count

        return result, 200
