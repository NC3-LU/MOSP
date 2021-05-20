API v2
======

The API version 2 uses the OpenAPI Specification for its documentation.
It is available `here <https://objects.monarc.lu/api/v2>`_.

If you want to query MOSP programmatically you can use
`PyMOSP <https://pypi.org/project/pymosp>`_, a Python library to access MOSP.

Clients using this API
----------------------

- `MONARC <https://www.monarc.lu>`_;
- `PyMOSP <https://pypi.org/project/PyMOSP>`_;
- `MONARC Stats Service <https://github.com/monarc-project/stats-service>`_ (with PyMOSP)


Examples
--------

Create a new object
```````````````````

With curl:

.. code-block:: bash

    object='[
        {
            "name": "New vulnerability",
            "description": "Description of this new object",
            "schema_id": 14,
            "org_id": 2,
            "json_object": {
                "code": "10",
                "description": "",
                "label": "Possibility of installing correction programmes, updates, patches, hotfixes, etc.",
                "language": "EN",
                "uuid": "69fbfe01-4591-11e9-9173-0800277f0572"
            },
            "licenses": [
                {
                    "license_id": "CC0-1.0"
                }
            ]
        }
    ]'

    curl -X POST "https://objects.monarc.lu/api/v2/object/" -H  "accept: application/json" -H  "X-API-KEY: <your-token>" -H  "Content-Type: application/json" -d $object


With PyMOSP:

.. code-block:: python

    import pymosp

    token = os.getenv("MOSP_TOKEN")
    mosp = pymosp.PyMOSP("https://objects.monarc.lu/api/v2/", token)

    new_objects = [
        {
            "name": "Possibility of installing correction programmes, updates, patches, hotfixes, etc.",
            "description": "",
            "licenses": [{"license_id": "CC0-1.0"}],
            "schema_id": 14,
            "org_id": 16,
            "json_object": {
                "code": "10",
                "description": "",
                "label": "Possibility of installing correction programmes, updates, patches, hotfixes, etc.",
                "language": "EN",
                "uuid": "69fbfe01-4591-11e9-9173-0800277f0572",
            }
        }
    ]

    r = mosp.add_objects(new_objects)
