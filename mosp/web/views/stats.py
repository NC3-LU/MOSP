from collections import defaultdict
from flask import Blueprint, render_template, jsonify

from mosp.models import Schema

import networkx as nx
from networkx.readwrite import json_graph


stats_bp = Blueprint("stats_bp", __name__, url_prefix="/stats")


def tree():
    return defaultdict(tree)


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            if "http" in node[kv]:
                yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


@stats_bp.route("/schemas/relations.json", methods=["GET"])
def digraph(software=None):
    G = nx.DiGraph()
    schemas_relations = tree()

    for schema in Schema.query.filter().all():
        # referrer_id = schema.json_schema.get("$id", None)
        node_start = G.add_node(schema.id, name=schema.name)
        referrers = findkeys(schema.json_schema.get("definitions", {}), "$ref")
        for referrer in list(referrers):
            ref = Schema.query.filter(
                Schema.json_schema[("$id")].astext == referrer
            ).first()
            if not ref:
                continue
            node_end = G.add_node(ref.id, name=ref.name)
            G.add_edge(schema.id, ref.id, type="ref")

    # json formatted data
    d = json_graph.node_link_data(G)  # node-link format to serialize

    return jsonify(d)
