#! /usr/bin/env python
#-*- coding: utf-8 -*-

from sqlalchemy import and_
from web.models import JsonObject

def check_duplicates(json_object):
    """Check for duplicates, by UUID, of the object given in parameter.
    """
    duplicates = []
    # extract the JSON part of the JsonObject
    json_obj = json_object.json_object
    if isinstance(json_obj, list):
        # if we have a list of JSON objects with a UUI for each of them
        for elem in json_obj:
            if elem.get('uuid', False):
                duplicate = JsonObject.query.filter(and_(
                    JsonObject.json_object[('uuid')].astext == elem['uuid']),
                    JsonObject.id != json_object.id)
                if duplicate.count() > 0:
                    duplicates.append(duplicate[0])

    if isinstance(json_obj, dict):
        # if we directly have an object
        if json_obj.get('uuid', False):
            duplicate = JsonObject.query.filter(and_(
                JsonObject.json_object[('uuid')].astext == json_obj['uuid']),
                JsonObject.id != json_object.id)
            if duplicate.count() > 0:
                duplicates.append(duplicate[0])

    return duplicates
