API v1
======

.. note::

    The API v1 is still available but is really discouraged to be used. It will be
    replaced. Use the :doc:`API v2 <./api-v2>`.


Endpoint for Schemas
--------------------

Getting the list of schemas:

.. code-block:: bash

    $ curl https://objects.monarc.lu/api/v1/schema

Getting information about a schema:

.. code-block:: bash

    $ https://objects.monarc.lu/api/v1/schema/13



Endpoint for JSON objects
-------------------------


Getting the list of JSON objects

.. code-block:: bash

    $ curl https://objects.monarc.lu/api/v1/json_object


Creating a new object
---------------------

.. code-block:: bash

    $ json_object='{}'
    $ curl -i \
        -H "Authorization: Token k8ZwQ6Cu1GRvJhO6517P9zcLroZzTZBYMwAoOfA6sm0MnGrBuxTzHGV6XfDWS_X__5w" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" -X POST \
        -d '{"name":"NIST","description":"Recommended Security Controls for Federal Information Systems and Organizations. (Rev.5)" ,"org_id":2,"json_object":'"$json_object"'}' \
        https://objects.monarc.lu/api/v1/json_object

    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 85
    Vary: Cookie

    {
      "message": "You are not allowed to create/edit object from this organization."
    }


.. code-block:: bash

    $ json_object='{}'
    $ curl -i \
        -H "Authorization: Token k8ZwQ6Cu1GRvJhO6517P9zcLroZzTZBYMwAoOfA6sm0MnGrBuxTzHGV6XfDWS_X__5w" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" -X POST \
        -d '{"name":"NIST","description":"Recommended Security Controls for Federal Information Systems and Organizations. (Rev.5)" ,"org_id":3,"json_object":'"$json_object"'}' \
        https://objects.monarc.lu/api/v1/json_object

    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 85
    Vary: Cookie
    Date: Thu, 21 Feb 2019 09:07:26 GMT

    {
      "message": "You must provide the id of a schema."
    }


.. code-block:: bash

    $ json_object='{}'
    $ curl -i \
        -H "Authorization: Token k8ZwQ6Cu1GRvJhO6517P9zcLroZzTZBYMwAoOfA6sm0MnGrBuxTzHGV6XfDWS_X__5w" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" -X POST \
        -d '{"name":"NIST","description":"Recommended Security Controls for Federal Information Systems and Organizations. (Rev.5)" ,"org_id":3,"schema_id":12,"json_object":'"$json_object"'}' \
        https://objects.monarc.lu/api/v1/json_object

    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 85
    Vary: Cookie
    Date: Thu, 21 Feb 2019 09:07:26 GMT

    {
      "message": "The object submitted is not validated by the schema."
    }


.. code-block:: bash

    $ json_object='{"label":"NIST SP 800-53","measures":[{"category": "Access Control","code": "AC-1","label": "Access Control Policy and Procedures","uuid": "ebf10522-0f57-4880-aa73-e28a206b7be4"}],"uuid": "cfd2cd50-95fa-4143-b0e5-794249bacae1","version": "5.0"}'
    $ curl -i \
        -H "Authorization: Token k8ZwQ6Cu1GRvJhO6517P9zcLroZzTZBYMwAoOfA6sm0MnGrBuxTzHGV6XfDWS_X__5w" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" -X POST \
        -d '{"name":"NIST","description":"Recommended Security Controls for Federal Information Systems and Organizations. (Rev.5)" ,"org_id":3,"schema_id":12,"json_object":'"$json_object"'}' \
        https://objects.monarc.lu/api/v1/json_object

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 2392
    Location: https://objects.monarc.lu/api/v1/json_object/30
    Vary: Accept, Cookie
    Content-Type: application/json
    Date: Thu, 21 Feb 2019 09:34:39 GMT


The content of the newly created object is also returned.


More complex queries
--------------------

Getting all objects owned by the MONARC organization:

.. code-block:: bash

    $ curl https://objects.monarc.lu/api/v1/json_object?q={"filters":[{"name":"organization","op":"has","val":{"name":"name","op":"eq","val": "MONARC"}}]}


Getting all schemas owned by the MONARC organization:

.. code-block:: bash

    $ curl https://objects.monarc.lu/api/v1/schema?q={"filters":[{"name":"organization","op":"has","val":{"name":"name","op":"eq","val":"MONARC"}}]}


Getting all the security referentials owned by the MONARC organization:

.. code-block:: bash

    $ curl https://objects.monarc.lu/api/v1/json_object?q={"filters":[{"name":"schema","op":"has","val":{"name":"name","op":"eq","val": "Security referentials"}},{"name":"organization","op":"has","val":{"name":"name","op":"eq","val": "MONARC"}}]}


Getting all the risks owned by the MONARC organization:

.. code-block:: bash

    $ curl https://objects.monarc.lu/api/v1/json_object?q={"filters":[{"name":"schema","op":"has","val":{"name":"name","op":"eq","val": "Risks"}},{"name":"organization","op":"has","val":{"name":"name","op":"eq","val": "MONARC"}}]}
