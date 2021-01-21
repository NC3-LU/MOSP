#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""This file contains functions useful with schemas.
"""

import json
from datetime import timezone
from flask import url_for
from feedgen.feed import FeedGenerator

from mosp.models import Schema
from mosp.bootstrap import application


def generate_schemas_atom_feed():
    """Generates an ATOM feed with the recent updated schemas."""
    recent_schemas = Schema.query.order_by(Schema.last_updated.desc()).limit(50)
    fg = FeedGenerator()
    fg.id(url_for("schemas_atom", _external=True))
    fg.title("Recent schemas published on MOSP")
    # fg.subtitle("")
    fg.link(href=application.config["INSTANCE_URL"], rel="self")
    fg.author(
        {
            "name": application.config["ADMIN_URL"],
            "email": application.config["ADMIN_EMAIL"],
        }
    )
    fg.language("en")
    for recent_schema in recent_schemas:
        fe = fg.add_entry()
        fe.id(
            url_for(
                "schema_bp.get", schema_id=recent_schema.id, _external=True
            )
        )
        fe.title(recent_schema.name)
        fe.description(recent_schema.description)
        fe.author({"name": recent_schema.organization.name})
        fe.content(
            json.dumps(
                recent_schema.json_schema,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )
        )
        fe.published(recent_schema.last_updated.replace(tzinfo=timezone.utc))
        fe.link(
            href=url_for(
                "schema_bp.definition", schema_id=recent_schema.id, _external=True
            )
        )
    atomfeed = fg.atom_str(pretty=True)
    return atomfeed
