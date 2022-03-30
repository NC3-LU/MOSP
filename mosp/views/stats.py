import re
from collections import Counter
from urllib.parse import urljoin

import networkx as nx
from flask import Blueprint
from flask import jsonify
from flask import render_template
from networkx.readwrite import json_graph

from mosp.bootstrap import application
from mosp.models import Event
from mosp.models import JsonObject
from mosp.models import Schema


stats_bp = Blueprint("stats_bp", __name__, url_prefix="/stats")


def findkeys(node, kv):
    """Generator to find the keys in graph represented as a dict structure
    or in a list."""
    if isinstance(node, list):
        for i in node:
            yield from findkeys(i, kv)
    elif isinstance(node, dict):
        if kv in node:
            if "http" in node[kv]:
                yield node[kv]
        for j in node.values():
            yield from findkeys(j, kv)


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

    # extract required informations from the events
    counter: Counter[str] = Counter()
    regex = re.compile(r"id=([0-9]+)\b")
    for event in events:
        result = regex.findall(event.subject)
        if not result:
            continue
        id = result[0]
        counter[id] += 1

    result = []
    for id, occurence in counter.most_common(10):
        obj = JsonObject.query.filter(JsonObject.id == id).first()
        if obj:
            try:
                uuid = obj.json_object.get("uuid", "")
            except Exception:
                uuid = ""
            try:
                language = obj.json_object.get("language", "")
            except Exception:
                language = ""
            result.append(
                {
                    "id": id,
                    "uuid": uuid,
                    "language": language,
                    "name": obj.name,
                    "count": occurence,
                }
            )

    return jsonify(result)


@stats_bp.route("/schemas/most-viewed.json", methods=["GET"])
def most_viewed_schemas():
    counter: Counter[str] = Counter()

    # look for uuid of schemas in JsonObject scope
    events = Event.query.filter(
        Event.scope == "JsonObject", Event.action == "apiv2.object_objects_list:GET"
    ).all()
    regex = re.compile(
        r"schema_uuid=([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\b"
    )
    for event in events:
        schema_uuid = event.subject.split()[2].replace("schema_uuid=", "")
        result = regex.findall(event.subject)
        if not result:
            continue
        schema_uuid = result[0]
        counter[schema_uuid] += 1

    # look for id of schemas in Schema scope
    events = Event.query.filter(
        Event.scope == "Schema", Event.action == "schema_bp.get:GET"
    ).all()
    regex = re.compile(r"id=([0-9]+)\b")
    for event in events:
        result = regex.findall(event.subject)
        if result:
            counter[result[0]] += 1

    result = []
    for uuid, occurence in counter.most_common(10):
        schema_uuid_absolute = urljoin(
            application.config["INSTANCE_URL"], "schema/def/" + str(uuid)
        )
        # load the object based on the UUID
        json_schema = Schema.query.filter(
            Schema.json_schema[("$id")].astext == schema_uuid_absolute,
        ).first()
        if not json_schema and uuid.isdigit():
            # if no corresponding schema found, load based on the id (here uuid is the
            # id, a digit)
            json_schema = Schema.query.filter(
                Schema.id == uuid,
            ).first()

        if json_schema:
            result.append(
                {
                    "id": uuid,
                    "name": json_schema.name,
                    "count": occurence,
                }
            )

    return jsonify(result)
