# kfx

[![PyPI version](https://badge.fury.io/py/kfx.svg)](https://badge.fury.io/py/kfx)
[![Build Status](https://travis-ci.org/e2fyi/kfx.svg?branch=master)](https://travis-ci.org/e2fyi/kfx)
[![Coverage Status](https://coveralls.io/repos/github/e2fyi/kfx/badge.svg?branch=master)](https://coveralls.io/github/e2fyi/kfx?branch=master)
[![Documentation Status](https://readthedocs.org/projects/kfx/badge/?version=latest)](https://kfx.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/kfx/month)](https://pepy.tech/project/kfx/month)

`kfx` is a python package with the namespace `kfx`. Currently, it provides the
following sub-packages:
    - `kfx.lib.vis`: Data models and helpers to generate ui metadata object for rendering vis in kubeflow pipeline UI.
    - `kfx.lib.utils`: Helpers to extend kubeflow pipeline tasks/containerOps.

> Documentation: [https://kfx.readthedocs.io](https://kfx.readthedocs.io).
> Repo: [https://github.com/e2fyi/kfx](https://github.com/e2fyi/kfx)

## Quick start

Installation
```bash
pip install kfx
```

## Usage

Generating ui metadata artifacts for kubeflow pipeline UI to render visualizations.
```py
import kfx.lib.vis as kfxvis
import kfx.lib.utils as kfxutils


@kfp.components.func_to_container_op
def test_op(
    mlpipeline_ui_metadata_file: OutputTextFile(str), markdown_file: OutputTextFile(str)
):

    import kfx.lib.utils as kfxutils
    import kfx.lib.vis as kfxvis


    # note that artifact name is `markdown` instead of `markdown_file`
    # `_file` and `_path` suffix are removed.
    markdown_file.write("### hello world")
    markdown_src = kfxutils.get_artifact_uri("markdown")

    # creates the ui metadata object
    mlpipeline_ui_metadata = kfxvis.kfp_ui_metadata(
        [kfxvis.markdown(source=markdown_src)]
    )
    # note that artifact name is `mlpipeline-ui-metadata` and not
    # `mlpipeline_ui_metadata_file`.
    mlpipeline_ui_metadata_file.write(kfxvis.asjson(mlpipeline_ui_metadata))

    # prints the artifact uri that will be saved by kfp to the artifactory.
    print(mlpipeline_ui_metadata.outputs[0].source)


# helper to decorate the task so that `kfx.lib.utils.get_artifact_uri` can be
# used to infer the uri of the artifact.
helper = kfxutils.ArtifactLocationHelper(
    scheme="minio", bucket="mlpipeline", key_prefix="artifacts/"
)

@kfp.dsl.pipeline()
def test_pipeline():
    """Test pipeline."""

    op: kfp.dsl.ContainerOp = test_op()
    # setup the required image and env vars, so that `kfx.lib.utils.get_artifact_uri`
    # can be used to infer artifact uri.
    op.apply(helper.set_envs())

```

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