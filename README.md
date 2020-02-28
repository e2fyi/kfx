# kfp-contrib

`kfp-contrib` is a python package with the namespace `kfp`.

## Developer guide

This project used:

- isort: to manage import order
- pylint: to manage general coding best practices
- flake8: to manage code complexity and coding best practices
- black: to manage formats and styles
- pydocstyle: to manage docstr style/format
- pytest/coverage: to manage unit tests and code coverage
- bandit: to find common security issues
- pyenv: to manage dev env: python version (3.6)
- pipenv: to manage dev env: python packages

Convention for unit tests are to suffix with `_test` and colocate with the actual
python module - i.e. `<module_name>_test.py`.

The version of the package is read from `version.txt` - i.e. please update the
appropriate semantic version (major -> breaking changes, minor -> new features, patch -> bug fix, postfix -> pre-release/post-release).

### `Makefile`:
```bash
# autoformat codes with docformatter, isort, and black
make format

# check style, formats, and code complexity
make check

# check style, formats, code complexity, and run unit tests
make test

# test everything including building the package and check the sdist
make test-all

# run unit test only
make test-only

# generate and update the requirements.txt and requirements-dev.txt
make requirements

# generate the docs with sphinx and autoapi extension
make docs

# generate distributions
make dists

# publish to pypi with twine (twine must be configured)
make publish
```