# MONARC Objects Sharing Platform

![Latest release](https://img.shields.io/github/release/CASES-LU/MOSP.svg?style=flat-square)
![License](https://img.shields.io/github/license/CASES-LU/MOSP.svg?style=flat-square)
![Contributors](https://img.shields.io/github/contributors/CASES-LU/MOSP.svg?style=flat-square)
![Stars](https://img.shields.io/github/stars/CASES-LU/MOSP.svg?style=flat-square)


## Presentation

[MOSP](https://github.com/CASES-LU/MOSP) is a platform to create, edit
and share JSON objects.

The goal is to gather security related JSON objects,
in the first place aimed to be used with
[MONARC](https://github.com/monarc-project/MonarcAppFO).

You can use any available schemas in order to create shareable JSON objects.
It is possible to keep an object private even if the goal is to promote
the sharing of information. Integration with third-party applications is
possible thanks to an API.

Official instance:  
[http://objects.monarc.lu](http://objects.monarc.lu)


## Installation

```bash
$ git clone https://github.com/CASES-LU/MOSP.git
$ cd MOSP/
$ npm install
$ pipenv install
$ pipenv shell
$ python src/manager.py db_create
$ python src/manager.py db_init
$ python src/manager.py import_licenses_from_spdx
$ python src/manager.py create_admin <username> <password>
$ python src/runserver.py
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
$ heroku run python src/manager.py import_licenses_from_spdx
$ heroku ps:scale web=1
```


## Documentation

[A documentation](https://www.monarc.lu/documentation/MOSP-documentation/)
is available on the MONARC website.


## License

This software is licensed under
[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html)


* Copyright (C) 2018-2019 Cédric Bonhomme
* Copyright (C) 2018-2019 SMILE gie securitymadein.lu

For more information, the [list of authors and contributors](AUTHORS.md) is
available.
