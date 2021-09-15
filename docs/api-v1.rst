API v1
======

.. note::

    The API v1 is available in read-only mode and is discouraged from being used.
    Use the :doc:`API v2 <./api-v2>`.


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
