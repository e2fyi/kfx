# kfx

[![PyPI version](https://badge.fury.io/py/kfx.svg)](https://badge.fury.io/py/kfx)
[![Build Status](https://travis-ci.org/e2fyi/kfx.svg?branch=master)](https://travis-ci.org/e2fyi/kfx)
[![Coverage Status](https://coveralls.io/repos/github/e2fyi/kfx/badge.svg?branch=master)](https://coveralls.io/github/e2fyi/kfx?branch=master)
[![Documentation Status](https://readthedocs.org/projects/kfx/badge/?version=latest)](https://kfx.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/kfx/month)](https://pepy.tech/project/kfx/month)

`kfx` is a python package with the namespace `kfx`. Currently, it provides the
following sub-packages

- `kfx.lib.dsl` - Extensions to yje kubeflow pipeline dsl.

- `kfx.lib.vis` - Data models and helpers to help generate the `mlpipeline-ui-metadata.json` required to render visualization in the kubeflow pipeline UI. See [Visualize Results in the Pipelines UI](https://www.kubeflow.org/docs/pipelines/sdk/output-viewer/)

> - Documentation: [https://kfx.readthedocs.io](https://kfx.readthedocs.io).
> - Repo: [https://github.com/e2fyi/kfx](https://github.com/e2fyi/kfx)

## Quick start

Installation

```bash
pip install kfx
```

## Usage

Example: Using `ArtifactLocationHelper` and `get_artifact_uri` to determine the
uri of your data artifact generated by the kubeflow pipeline task.

> `kfx.dsl.ArtifactLocationHelper` is a helper to modify the kubeflow pipeline task
> so that you can use `kfx.dsl.get_artifact_uri` to get the uri of your data
> artifact that will be generated inside the task.

```python
import kfp.components
import kfp.dsl
import kfx.dsl


# creates the helper that has the argo configs (tells you how artifacts will be stored)
# see https://github.com/argoproj/argo/blob/master/docs/workflow-controller-configmap.yaml
helper = kfx.dsl.ArtifactLocationHelper(
    scheme="minio", bucket="mlpipeline", key_prefix="artifacts/"
)

@kfp.components.func_to_container_op
def test_op(
    mlpipeline_ui_metadata: OutputTextFile(str), markdown_data_file: OutputTextFile(str)
):
    "A test kubeflow pipeline task."

    import json

    import kfx.dsl
    import kfx.vis
    import kfx.vis.vega

    data = [
        {"a": "A", "b": 28},
        {"a": "B", "b": 55},
        {"a": "C", "b": 43},
        {"a": "D", "b": 91},
        {"a": "E", "b": 81},
        {"a": "F", "b": 53},
        {"a": "G", "b": 19},
        {"a": "H", "b": 87},
        {"a": "I", "b": 52},
    ]
    vega_data_file.write(json.dumps(data))

    # `KfpArtifact` provides the reference to data artifact created
    # inside this task
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "description": "A simple bar chart",
        "data": {
            "url": kfx.dsl.KfpArtifact("vega_data_file"),
            "format": {"type": "json"},
        },
        "mark": "bar",
        "encoding": {
            "x": {"field": "a", "type": "ordinal"},
            "y": {"field": "b", "type": "quantitative"},
        },
    }

    # write the markdown to the `markdown-data` artifact
    markdown_data_file.write("### hello world")

    # creates an ui metadata object
    ui_metadata = kfx.vis.kfp_ui_metadata(
        # Describes the vis to generate in the kubeflow pipeline UI.
        [
            # markdown vis from a markdown artifact.
            # `KfpArtifact` provides the reference to data artifact created
            # inside this task
            kfx.vis.markdown(kfx.dsl.KfpArtifact("markdown_data_file")),
            # a vega web app from the vega data artifact.
            kfx.vis.vega.vega_web_app(spec),
        ]
    )

    # writes the ui metadata object as the `mlpipeline-ui-metadata` artifact
    mlpipeline_ui_metadata.write(kfx.vis.asjson(ui_metadata))

    # prints the uri to the markdown artifact
    print(ui_metadata.outputs[0].source)


@kfp.dsl.pipeline()
def test_pipeline():
    "A test kubeflow pipeline"

    op: kfp.dsl.ContainerOp = test_op()

    # modify kfp operator with artifact location metadata through env vars
    op.apply(helper.set_envs())

```

Example: Using [pydantic](https://pydantic-docs.helpmanual.io/) data models to generate
[`mlpipeline_ui_metadata`](https://www.kubeflow.org/docs/pipelines/sdk/output-viewer/).

> `kfx.vis` has helper functions (with corresponding hints) to describe and create a
> [`mlpipeline_ui_metadata.json`](https://www.kubeflow.org/docs/pipelines/sdk/output-viewer/)
> file (required by kubeflow pipeline UI to render any visualizations).

```python
import kfp.components
import kfx.vis

from kfx.vis.enums import KfpStorage


@func_to_container_op
def some_op(mlpipeline_ui_metadata: OutputTextFile(str)):
    "kfp operator that provides metadata for visualizations."

    mlpipeline_ui_metadata = kfx.vis.kfp_ui_metadata(
        [
            # creates a confusion matrix vis
            kfx.vis.confusion_matrix(
                source="gs://your_project/your_bucket/your_cm_file",
                labels=["True", "False"],
            ),
            # creates a markdown with inline source
            kfx.vis.markdown(
                "# Inline Markdown: [A link](https://www.kubeflow.org/)",
                storage="inline",
            ),
            # creates a markdown with a remote source
            kfx.vis.markdown(
                "gs://your_project/your_bucket/your_markdown_file",
            ),
            # creates a ROC curve with a remote source
            kfx.vis.roc(
                "gs://your_project/your_bucket/your_roc_file",
            ),
            # creates a Table with a remote source
            kfx.vis.table(
                "gs://your_project/your_bucket/your_csv_file",
                header=["col1", "col2"],
            ),
            # creates a tensorboard viewer
            kfx.vis.tensorboard(
                "gs://your_project/your_bucket/logs/*",
            ),
            # creates a custom web app from a remote html file
            kfx.vis.web_app(
                "gs://your_project/your_bucket/your_html_file",
            ),
        ]
    )

    # write ui metadata so that kubeflow pipelines UI can render visualizations
    mlpipeline_ui_metadata.write(kfx.vis.asjson(mlpipeline_ui_metadata))
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