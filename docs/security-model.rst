Security model
==============

Permissions
-----------

Schemas
```````

You can only create an object in one of the organizations your account is linked to.

In order to edit a schema your account must be linked to the owning organization of the
schema.


Objects
```````

You can only create an object in one of the organizations your account is linked to.
Since all schemas are public you can instantiate a new object with the schema of your
choice.

In order to edit an object your account should be linked to the owning organization of
this object.


Organizations
`````````````

There are two types of organizations:

- with membership restriction: members are managed by an admin of the platform;
- without membership restriction:  members can join the organization without invitation.


Users
-----

Users are identified with their login which is unique across the platform.
The email address is voluntary not unique.

Each user has an API key.

If the self-registration mode is set to True for a MOSP instance, it will be
possible for anyone to create an account on the platform. The account will be
effective after an email verification.
