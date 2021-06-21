#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""This file contains functions useful with JsonObject objects.
"""

import json
import difflib
import tarfile
from io import BytesIO
from datetime import timezone
from sqlalchemy import and_
from flask import url_for
from feedgen.feed import FeedGenerator

from mosp.models import JsonObject
from mosp.bootstrap import application


def check_duplicates(json_object):
    """Check for duplicates, by UUID, of the object given in parameter."""
    duplicates = []
    # extract the JSON part of the JsonObject
    json_obj = json_object.json_object
    if isinstance(json_obj, list):
        # if we have a list of JSON objects with a UUI for each of them
        for elem in json_obj:
            if elem.get("uuid", False):
                duplicate = JsonObject.query.filter(
                    and_(JsonObject.json_object[("uuid")].astext == elem["uuid"]),
                    JsonObject.id != json_object.id,
                )
                if duplicate.count() > 0:
                    duplicates.append(duplicate[0])

    if isinstance(json_obj, dict):
        # if we directly have an object
        if json_obj.get("uuid", False):
            duplicate = JsonObject.query.filter(
                and_(JsonObject.json_object[("uuid")].astext == json_obj["uuid"]),
                JsonObject.id != json_object.id,
            )
            if duplicate.count() > 0:
                duplicates.append(duplicate[0])

    return duplicates


def generate_diff(version_before, version_after):
    """Generate a dif table between two revision of an object."""
    before_json = json.dumps(
        version_before.json_object,
        ensure_ascii=False,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    ).split("\n")
    after_json = json.dumps(
        version_after.json_object,
        ensure_ascii=False,
        sort_keys=True,
        indent=4,
        separators=(",", ": "),
    ).split("\n")

    table = difflib.HtmlDiff().make_table(before_json, after_json)

    table = table.replace(
        "<colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>",
        '<colgroup style="width: 2%;"></colgroup> <colgroup style="width: 2%;"></colgroup> <colgroup style="width: 46%;"></colgroup>',
        1
    )
    table = table.replace(
        "<colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>",
        '<colgroup style="width: 2%;"></colgroup> <colgroup style="width: 2%;"></colgroup> <colgroup style="width: 46%;"></colgroup>',
        1
    )

    return table


def generate_misp_galaxy_cluster(json_object):
    """Generates a MISP galaxy and cluster from an object."""
    # Creation of the galaxy
    # (https://github.com/MISP/misp-galaxy/blob/master/schema_galaxies.json)
    galaxy = {
        "uuid": json_object.json_object.get("uuid", ""),
        "name": json_object.name,
        "description": json_object.description,
        # let assume that for us the type is the schema name:
        "type": json_object.schema.name,
        "version": json_object.json_object.get("version", ""),
    }
    # Creation of the cluster
    # (https://github.com/MISP/misp-galaxy/blob/master/schema_clusters.json)
    cluster = {
        "uuid": json_object.json_object.get("uuid", ""),
        "name": json_object.name,
        "description": json_object.description,
        "version": json_object.json_object.get("version", ""),
        "type": json_object.schema.name,
        "authors": json_object.json_object.get("authors", []),
        # let assume that for us the source is the organization name:
        "source": json_object.organization.name,
        # and the category is the schema which is validating the object:
        "category": json_object.schema.name,
        "values": [],
    }
    for value in json_object.json_object.get("values", []):
        cluster["values"].append(
            {
                "uuid": value.pop("uuid", ""),
                "value": value.pop("code", ""),
                "description": value.pop("label")
                if value.get("label", False)
                else value.pop("description", ""),
                "meta": value,
            }
        )
    return (galaxy, cluster)


def generate_tar_gz_archive(galaxy, cluster):
    """Generates a tar.gz archive from a MISP galaxy (galaxy and a cluster)."""
    out = BytesIO()
    tar = tarfile.open(mode="w:gz", fileobj=out)

    galaxy_str = json.dumps(galaxy)
    cluster_str = json.dumps(cluster)

    # t = tarfile.TarInfo("galaxy")
    # t.type = tarfile.DIRTYPE
    # tar.addfile(t)

    tarinfo = tarfile.TarInfo("{}-galaxy.json".format(galaxy["name"].replace(" ", "_")))
    tarinfo.size = len(galaxy_str)
    tar.addfile(tarinfo, BytesIO(galaxy_str.encode()))

    tarinfo = tarfile.TarInfo(
        "{}-cluster.json".format(cluster["name"].replace(" ", "_"))
    )
    tarinfo.size = len(cluster_str)
    tar.addfile(tarinfo, BytesIO(cluster_str.encode()))

    tar.close()

    return out.getvalue()


def generate_objects_atom_feed():
    """Generates an ATOM feed with the recent updated objects."""
    recent_objects = JsonObject.query.order_by(JsonObject.last_updated.desc()).limit(50)
    fg = FeedGenerator()
    fg.id(url_for("objects_atom", _external=True))
    fg.title("Recent objects published on MOSP")
    # fg.subtitle("")
    fg.link(href=application.config["INSTANCE_URL"], rel="self")
    fg.author(
        {
            "name": application.config["ADMIN_URL"],
            "email": application.config["ADMIN_EMAIL"],
        }
    )
    fg.language("en")
    for recent_object in recent_objects:
        fe = fg.add_entry()
        fe.id(
            url_for(
                "object_bp.get_json_object", object_id=recent_object.id, _external=True
            )
        )
        fe.title(recent_object.name)
        fe.description(recent_object.description)
        fe.author({"name": recent_object.organization.name})
        fe.content(
            json.dumps(
                recent_object.json_object,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )
        )
        fe.published(recent_object.last_updated.replace(tzinfo=timezone.utc))
        fe.link(
            href=url_for(
                "object_bp.get_json_object", object_id=recent_object.id, _external=True
            )
        )
    atomfeed = fg.atom_str(pretty=True)
    return atomfeed
