MOSP Changelog
==============

## 0.13 (2020-04-23)

### News

- added new API which is returning data about relations between JSON schemas
  hosted on the platform. These data are generated with the networkx Python
  library and returned as JSON object compatible with D3.js;
- added a new D3.js graph which is using the new API;
- added a new view which presents all relations (refs) of a JSON object (self,
  external and recursive references are supported).

### Improvements

- various minor improvements and bug fixes.


## 0.12 (2020-04-09)

### News

- added email attribute for users;
- added password recovery feature;
- added a view which returns the definition of a schema (text/plain). This is
  used for external references in JSON schemas.

### Improvements

- improved generation of MISP clusters from an object: all values (properties)
  not directly useful for the context of the current schema in MONARC are
  assigned to the key 'meta';
- migrate form Flask-Script to the built-in integration of the click command
  line interface of Flask;
- updated JSON-editor for the JSON objects and added a new simple editor for the
  JSON schemas;
- various minor improvements and bug fixes.


## 0.11 (2020-02-03)

- fixed an issue related to the authentication via the API (which is used by
  the JSON editor);
- improvements to the authentication service.


## 0.10 (2019-12-19)

- added token based authentication for the API. Documentation is available:
  https://github.com/CASES-LU/MOSP-documentation/blob/master/index.adoc#using-the-api
- the project is now using poetry.


## 0.9 (2019-12-12)

- major improvements to the structure of the backend and to the models;
- introduction of tests with pytest;
- now using GitHub test workflow (GitHub Actions);
- added app.json file for easy deployment with the Heroku button.


## 0.8 (2019-11-28)

- Add a warning when the UUID of new a object is already taken (#14);
- Generation of MISP galaxies and clusters based on an object from MOSP (#15);
- Add a button in order to help the user generate a UUID easily (#16);
- Added a way to list the recently created/updated objects for an administrator;
- Added shortcuts to create new users and organizations. Simplify the creation
  of new users/organizations;
- The footprint of objects is no more displayed;
- Improved the performances on JsonObject GET many by removing useless
  attributes from the result;
- updated Bootstrap to the version 4.4.


## 0.7 (2019-09-12)

- it is now possible to specify links between objects when creating a new one;
- it is now possible to access to an object with its id or with the UUID of the
  JSONB object attribute of this object (objects.monarc.lu/object/<UUID>);
- it is now possible to copy an object from one organization to an other (#11);
- it is now possible to download all JSON objects validated by a schema.
  Objects are returned in a flattened list;
- the contact e-mail address from the terms page is now using the one defined
  in the configuration file;
- updated version of json-editor used in the project.


## 0.6 (2019-03-12)

- added the possibility to link objects (#8);
- the footprint (SHA 256 sum of objects is now displayed);
- added the possibility to copy an object to the clipboard;
- added a terms page;
- improved the organization page;
- improved the admin/users page;
- minor UI fixes.


## 0.5 (2019-02-24)

- major improvements to the API. It is now possible to create a valid JSON
  object programmatically with the HTTP POST method. The validity of the
  submitted object is checked against the specified JSON schema;
- the project has now an official logo (#7);
- a human.txt file has been added (https://objects.monarc.lu/human.txt).
- various fixes and UI improvements. All views have been improved;
- a documentation is now available and will be improved
  (https://www.monarc.lu/documentation/MOSP-documentation)


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
