MOSP Changelog
==============

## 0.4 (2018-10-05)

- it is now possible to select one or several licenses for an object (#2). A
  script is provided in order to initialize the database with licenses from
  https://spdx.org/licenses/licenses.json;
- the values of a JSON object can now be exported to a CSV file;
- the management of permissions has been improved;
- added a new profile page for users;
- various fixes and UI improvements.

## 0.3.0 (2018-06-01)

- new Web interface to list, create and edit JSON schemas;
- improved management of users. It is now possible to block a user;
- translations improvements;
- various UI improvements.

## 0.2.0 (2018-05-30)

- the JSONB PostgreSQL type is now used instead of the JSON type;
- the JSON editor has been upgraded and is now properly working with
  Bootstrap 4.1;
- the interface to edit JSON data has been revamped and is a lot cleaner;
- DataTables is now used for all tables;
- a new interface displays all the JSON schemas in the organization(s) of a
  user;
- a panel to manage users of the platform has been added;
- the Web interface is internationalized in French (80% of strings are actually
  translated);
- various UI improvements.

## 0.1.0 (2018-05-13)

- first beta release of MOSP;
- basic features are implemented: management of JSON objects, management of
  JSON schemas, management of users and organizations;
- it is possible to edit a JSON object with a JSON editor which is generated
  thanks to the JSON schemas;
- a basic API let the user interact programmatically with the JSON objects.
