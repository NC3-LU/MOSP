#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""This file contains functions useful with collections.
"""

from datetime import timezone
from flask import url_for
from feedgen.feed import FeedGenerator

from mosp.models import Collection
from mosp.bootstrap import application


def generate_collections_atom_feed():
    """Generates an ATOM feed with the recent updated collections."""
    recent_collections = Collection.query.order_by(
        Collection.last_updated.desc()
    ).limit(50)
    fg = FeedGenerator()
    fg.id(url_for("collections_atom", _external=True))
    fg.title("Recent collections published on MOSP")
    # fg.subtitle("")
    fg.link(href=application.config["INSTANCE_URL"], rel="self")
    fg.author(
        {
            "name": application.config["ADMIN_URL"],
            "email": application.config["ADMIN_EMAIL"],
        }
    )
    fg.language("en")
    for recent_collection in recent_collections:
        fe = fg.add_entry()
        fe.id(
            url_for(
                "collection_bp.get",
                collection_uuid=recent_collection.uuid,
                _external=True,
            )
        )
        fe.title(recent_collection.name)
        fe.description(recent_collection.description)
        fe.published(recent_collection.last_updated.replace(tzinfo=timezone.utc))
        fe.link(
            href=url_for(
                "collection_bp.get",
                collection_uuid=recent_collection.uuid,
                _external=True,
            )
        )
    atomfeed = fg.atom_str(pretty=True)
    return atomfeed
