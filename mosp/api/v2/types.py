#! /usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Any
from typing_extensions import TypedDict


class MetaDataType(TypedDict):
    """Defines a type for a question with user answers"""

    count: int
    offset: int
    limit: int


class ResultType(TypedDict):
    """Defines a type for a question with user answers"""

    data: List[Any]
    metadata: MetaDataType
