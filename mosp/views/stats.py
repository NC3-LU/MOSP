from collections import Counter
from flask import Blueprint, jsonify, render_template

from mosp.models import Schema, JsonObject, Event

import networkx as nx
from networkx.readwrite import json_graph


stats_bp = Blueprint("stats_bp", __name__, url_prefix="/stats")


def findkeys(node, kv):
    """Generator to find the keys in graph represented as a dict structure
    or in a list."""
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


@stats_bp.route("/", methods=["GET"])
def index():
    """Display some stats."""
    return render_template("stats.html")


@stats_bp.route("/schemas/relations.json", methods=["GET"])
def digraph(software=None):
    G = nx.DiGraph()

    for schema in Schema.query.filter().all():
        # referrer_id = schema.json_schema.get("$id", None)
        G.add_node(schema.id, name=schema.name, description=schema.description)
        referrers = findkeys(schema.json_schema.get("definitions", {}), "$ref")
        for referrer in list(referrers):
            ref = Schema.query.filter(
                Schema.json_schema[("$id")].astext == referrer
            ).first()
            if not ref:
                continue
            G.add_node(ref.id, name=ref.name, description=ref.description)
            G.add_edge(schema.id, ref.id, type="ref")

    # json formatted data
    d = json_graph.node_link_data(G)  # node-link format to serialize

    return jsonify(d)


@stats_bp.route("/objects/most-viewed.json", methods=["GET"])
def most_viewed_objects():
    events = Event.query.filter(
        Event.scope == "JsonObject", Event.action == "object_bp.view:GET"
    ).all()

    counter = Counter()
    for event in events:
        id = event.subject.split()[0].replace("id=", "")
        # uuid = event.subject.split()[1]
        counter[id] += 1

    result = {}
    for id, occurence in counter.most_common(20):
        obj = JsonObject.query.filter(JsonObject.id == id).first()
        if obj:
            result[id] = {
                "uuid": obj.json_object.get("uuid", ""),
                "language": obj.json_object.get("langauge", ""),
                "name": obj.name,
                "count": occurence,
            }

    return jsonify(result)
