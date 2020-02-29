"""Tests for kfx.lib.utils."""
from typing import List

import kfp.dsl
import kfp.compiler
import kfp.components
import kubernetes.client as k8s_client

from kfp.compiler import Compiler
from kfp.components import OutputTextFile

import kfx.lib.utils as kfxutils


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
            kfxutils.set_workflow_env(
                kfxutils.WorkflowVars("WORKFLOW_NAME", template="{{workflow.name}}")
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
        op.apply(kfxutils.set_pod_metadata_envs())

        assert is_envs_similar(op.container.env, expected)

    outfile = tmp_path / "pipeline.yaml"
    Compiler().compile(test_pipeline, str(outfile))


def test_artifact_location_helper(tmp_path):
    expected_envs = [
        {"name": "WORKFLOW_ARTIFACT_PREFIX", "value": "test-op", "value_from": None},
        {
            "name": "WORKFLOW_ARTIFACT_LOCATION",
            "value": "minio://mlpipeline/artifacts/{{workflow.name}}/{{pod.name}}",
            "value_from": None,
        },
    ]

    helper = kfxutils.ArtifactLocationHelper(
        scheme="minio", bucket="mlpipeline", key_prefix="artifacts/"
    )

    @kfp.components.func_to_container_op
    def test_op(
        mlpipeline_ui_metadata: OutputTextFile(str), markdown_file: OutputTextFile(str)
    ):

        import kfx.lib.utils as kfxutils
        import kfx.lib.vis as kfxvis

        markdown_file.write("### hello world")
        ui_metadata = kfxvis.kfp_ui_metadata(
            [kfxvis.markdown(kfxutils.get_artifact_uri("markdown"))]
        )
        mlpipeline_ui_metadata.write(kfxvis.asjson(ui_metadata))
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
