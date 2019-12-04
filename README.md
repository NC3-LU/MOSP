# MONARC Objects Sharing Platform

![MOSP logo](https://github.com/CASES-LU/MOSP/blob/master/mosp/static/img/logo-large.png)

[![Latest release](https://img.shields.io/github/release/CASES-LU/MOSP.svg?style=flat-square)](https://github.com/CASES-LU/MOSP/releases/latest)
![License](https://img.shields.io/github/license/CASES-LU/MOSP.svg?style=flat-square)
![Contributors](https://img.shields.io/github/contributors/CASES-LU/MOSP.svg?style=flat-square)
![Stars](https://img.shields.io/github/stars/CASES-LU/MOSP.svg?style=flat-square)
[![Workflow](https://github.com/CASES-LU/MOSP/workflows/Python%20application/badge.svg?style=flat-square)](https://github.com/CASES-LU/MOSP/actions?query=workflow%3A%22Python+application%22)


## Presentation

[MOSP](https://github.com/CASES-LU/MOSP) is a platform for creating, editing
and sharing JSON objects of any type.

The goal is to gather security related JSON objects, in the first place aimed
to be used with [MONARC](https://github.com/monarc-project/MonarcAppFO).
You can use any available schemas in order to create new JSON objects or you
can create new JSON schemas.

It is possible to interact with MOSP programmatically thanks to its API.

As example you can have a look at [official instance](https://objects.monarc.lu)
operated by [CASES](https://github.com/CASES-LU) and more particularly the
[objects](https://objects.monarc.lu/organization/MONARC) shared by the
[MONARC project](https://github.com/monarc-project).


## Installation

```bash
$ git clone https://github.com/CASES-LU/MOSP.git
$ cd MOSP/
$ npm install
$ pipenv install
$ pipenv shell
$ python mosp/manager.py db_create
$ python mosp/manager.py db_init
$ python mosp/manager.py import_licenses_from_spdx
$ python mosp/manager.py create_admin <username> <password>
$ pybabel compile -d mosp/web/translations
$ python mosp/runserver.py
```


### Deploy on Heroku

```bash
$ heroku create --region eu <name-of-your-instance>
$ heroku addons:add heroku-postgresql:hobby-dev
$ heroku config:set APPLICATION_SETTINGS='heroku.cfg'
$ heroku buildpacks:add --index 1 heroku/python
$ heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-nodejs
$ git push heroku master
$ heroku run init
$ heroku run python mosp/manager.py import_licenses_from_spdx
$ heroku ps:scale web=1
```


## Contributing

Contributions are welcome and there are many ways to participate to the
project. You can contribute to MOSP by:

- reporting bugs;
- suggesting enhancements or new features;
- improving the documentation;
- creating new objects on [our instance](https://objects.monarc.lu).

Feel free to fork the code, play with it, make some patches and send us
pull requests.

There is one main branch: what we consider as stable with frequent updates as
hot-fixes.

Features are developed in separated branches and then regularly merged into the
master stable branch.


## Documentation

A [documentation](https://www.monarc.lu/documentation/MOSP-documentation)
is available on the MONARC website.


## License

This software is licensed under
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html)


* Copyright (C) 2018-2019 Cédric Bonhomme
* Copyright (C) 2018-2019 SMILE gie securitymadein.lu

For more information, the [list of authors and contributors](AUTHORS.md) is
available.
