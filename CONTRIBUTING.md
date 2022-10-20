Contributions are welcome and there are many ways to participate to the
project.

Before starting to contribute please install the Git hook scripts:

```bash
$ git clone https://github.com/NC3-LU/MOSP
$ cd MOSP/
$ poetry install
$ pre-commit install
```

You can contribute to MOSP by:

- reporting bugs;
- suggesting enhancements or new features;
- improving the documentation;
- creating new objects on [our instance](https://objects.monarc.lu).

Feel free to fork the code, play with it, make some patches and send us pull requests.

There is one main branch: what we consider as stable with frequent updates as
hot-fixes.

Features are developed in separated branches and then regularly merged into the
master stable branch.

If your contribution require some documentation changes, a pull-request in order
to update the documentation is strongly recommended.

Please, do not open directly a GitHub issue if you think you have found a
security vulnerability. See our
[security policy](https://github.com/NC3-LU/MOSP/security/policy)
page.

[Flask](https://flask.palletsprojects.com) is used for the backend.
Please use [black](https://github.com/psf/black) for the syntax of your Python code.

[Vanilla JS](http://vanilla-js.com) is the JavaScript framework used.


## Building the documentation

Please provide documentation when changing, removing, or adding features.
Documentation resides in the project's [docs](docs/) folder.

```bash
$ poetry install
$ make doc
```

It will generate the main documentation.
If you want a documenation per tags and development branches:

```bash
$ poetry install
$ make multidoc
```


The documentation is available online
[here](https://www.monarc.lu/documentation/MOSP-documentation/).
