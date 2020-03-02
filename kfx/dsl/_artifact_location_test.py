"""Tests for kfx.lib.utils."""
import os

from typing import List

import kfp.dsl
import kfp.compiler
import kfp.components
import kubernetes.client as k8s_client

from kfp.compiler import Compiler
from kfp.components import OutputTextFile

import kfx.dsl._artifact_location


def is_envs_similar(
    envs: List[k8s_client.V1EnvVar], expected_envs: List[k8s_client.V1EnvVar]
) -> bool:

    return [env.to_dict() for env in envs] == expected_envs


def test_set_workflow_name(tmp_path):
    expected = [
        {"name": "WORKFLOW_NAME", "value": "{{workflow.name}}", "value_from": None}
    ]

    @kfp.components.func_to_container_op
    def test_op():
        import os

        print(os.environ.get("WORKFLOW_NAME"))

    @kfp.dsl.pipeline()
    def test_pipeline():
        op: kfp.dsl.ContainerOp = test_op()
        op.apply(
            kfx.dsl._artifact_location.set_workflow_env(
                kfx.dsl._artifact_location.WorkflowVars(
                    "WORKFLOW_NAME", template="{{workflow.name}}"
                )
            )
        )

        assert is_envs_similar(op.container.env, expected)

    outfile = tmp_path / "pipeline.yaml"
    Compiler().compile(test_pipeline, str(outfile))


def test_set_pod_metadata(tmp_path):
    expected = [
        {
            "name": "POD_NAME",
            "value": None,
            "value_from": {
                "config_map_key_ref": None,
                "field_ref": {"api_version": None, "field_path": "metadata.name"},
                "resource_field_ref": None,
                "secret_key_ref": None,
            },
        },
        {
            "name": "NAMESPACE",
            "value": None,
            "value_from": {
                "config_map_key_ref": None,
                "field_ref": {"api_version": None, "field_path": "metadata.namespace"},
                "resource_field_ref": None,
                "secret_key_ref": None,
            },
        },
        {
            "name": "NODE_NAME",
            "value": None,
            "value_from": {
                "config_map_key_ref": None,
                "field_ref": {"api_version": None, "field_path": "spec.nodeName"},
                "resource_field_ref": None,
                "secret_key_ref": None,
            },
        },
    ]

    @kfp.components.func_to_container_op
    def test_op():
        import os

        print(os.environ.get("WORKFLOW_NAME"))

    @kfp.dsl.pipeline()
    def test_pipeline():
        op: kfp.dsl.ContainerOp = test_op()
        op.apply(kfx.dsl._artifact_location.set_pod_metadata_envs())

        assert is_envs_similar(op.container.env, expected)

    outfile = tmp_path / "pipeline.yaml"
    Compiler().compile(test_pipeline, str(outfile))


def test_artifact_location_helper(tmp_path):
    expected_envs = [
        {"name": "WORKFLOW_ARTIFACT_STORAGE", "value": "minio", "value_from": None},
        {"name": "WORKFLOW_ARTIFACT_BUCKET", "value": "mlpipeline", "value_from": None},
        {
            "name": "WORKFLOW_ARTIFACT_KEY_PREFIX",
            "value": "artifacts/{{workflow.name}}/{{pod.name}}",
            "value_from": None,
        },
        {"name": "WORKFLOW_ARTIFACT_PREFIX", "value": "test-op", "value_from": None},
    ]

    helper = kfx.dsl._artifact_location.ArtifactLocationHelper(
        scheme="minio", bucket="mlpipeline", key_prefix="artifacts/"
    )

    @kfp.components.func_to_container_op
    def test_op(
        mlpipeline_ui_metadata: OutputTextFile(str),
        markdown_data_file: OutputTextFile(str),
        vega_data_file: OutputTextFile(str),
    ):
        import json

        import kfx.dsl
        import kfx.vis
        import kfx.vis.vega

        data = {
            "data": [
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
        }
        vega_data_file.write(json.dumps(data))

        spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
            "description": "A simple bar chart",
            "data": {
                "url": kfx.dsl.KfpArtifact("vega_data_file"),
                "format": {"type": "json", "property": "data"},
            },
            "mark": "bar",
            "encoding": {
                "x": {"field": "a", "type": "ordinal"},
                "y": {"field": "b", "type": "quantitative"},
            },
        }

        markdown_data_file.write("### hello world")
        ui_metadata = kfx.vis.kfp_ui_metadata(
            [
                kfx.vis.markdown(kfx.dsl.KfpArtifact("markdown_data_file")),
                kfx.vis.vega.vega_web_app(spec),
            ]
        )
        mlpipeline_ui_metadata.write(kfx.vis.asjson(ui_metadata))
        print(ui_metadata.outputs[0].source)

    @kfp.dsl.pipeline()
    def test_pipeline():
        op: kfp.dsl.ContainerOp = test_op()
        op.apply(helper.set_envs())

        assert is_envs_similar(op.container.env, expected_envs)

    outfile = tmp_path / "pipeline.yaml"
    Compiler().compile(test_pipeline, str(outfile))
    # print(outfile.read_text())
    # assert False


def test_kfp_artifact():

    os.environ[
        kfx.dsl._artifact_location.ArtifactLocationHelper.artifact_storage_env
    ] = "gcs"
    os.environ[
        kfx.dsl._artifact_location.ArtifactLocationHelper.artifact_bucket_env
    ] = "your_bucket"
    os.environ[
        kfx.dsl._artifact_location.ArtifactLocationHelper.artifact_key_prefix_env
    ] = "pipelines/artifact"
    os.environ[
        kfx.dsl._artifact_location.ArtifactLocationHelper.artifact_prefix_env
    ] = "test-task"

    assert (
        str(kfx.dsl.KfpArtifact("some_artifact_file"))
        == "gcs://your_bucket/pipelines/artifact/test-task-some_artifact.tgz"
    )

    assert (
        str(kfx.dsl.KfpArtifact("some_artifact_path"))
        == "gcs://your_bucket/pipelines/artifact/test-task-some_artifact.tgz"
    )
