"""Utils."""
import os
import os.path

from typing import Callable, NamedTuple

import kfp.dsl
import kfp.compiler._k8s_helper as _kfp_k8s_helper

from kubernetes import client as k8s_client

DEFAULT_KEY_FORMAT = "{{workflow.name}}/{{pod.name}}"


class WorkflowVars(NamedTuple):
    """Describes a templated workflow environment variable."""

    name: str
    template: str


def set_workflow_env(
    workflow_vars: WorkflowVars = WorkflowVars(
        name="WORKFLOW_DEFAULT_KEY_FORMAT", template="{{workflow.name}}/{{pod.name}}"
    )
) -> Callable[[kfp.dsl.ContainerOp], kfp.dsl.ContainerOp]:
    """Setup a kfp op to pass in the workflow variables as an environment var.

    See https://github.com/argoproj/argo/blob/master/docs/variables.md

    Example::

        import kfp
        import kfx.lib.utils as kfxutils

        from kfp.components import func_to_container_op

        @func_to_container_op
        def echo_workflow_vars():
            import os

            print(os.environ.get("WORKFLOW_NAME"))


        @kfp.dsl.pipeline()
        def simple_pipeline():
            op = echo_workflow_vars()
            op.apply(kfxutils.set_workflow_env(
                kfxutils.WorkflowVars("WORKFLOW_NAME", template="{{workflow.name}}")
            ))

    Args:
        name (str, optional): Env var name to pass in.
            Defaults to "WORKFLOW_DEFAULT_KEY_FORMAT".
        value (str, optional): Template string with argo workflow variables.
            Defaults to "{{workflow.name}}/{{pod.name}}".

    Returns:
        Callable[[kfp.dsl.ContainerOp], kfp.dsl.ContainerOp]: kfp op.
    """

    def apply_workflow_name_env(task: kfp.dsl.ContainerOp) -> kfp.dsl.ContainerOp:
        task.container.add_env_variable(
            k8s_client.V1EnvVar(name=workflow_vars.name, value=workflow_vars.template)
        )
        return task

    return apply_workflow_name_env


def set_pod_metadata_envs(
    pod_name: str = "POD_NAME",
    namespace: str = "NAMESPACE",
    node_name: str = "NODE_NAME",
) -> Callable[[kfp.dsl.ContainerOp], kfp.dsl.ContainerOp]:
    """Setup a kfp op to pass in the pod name, namespace, and node name as env
    var.

    Example::

        import kfp
        import kfx.lib.utils as kfxutils

        from kfp.components import func_to_container_op

        @func_to_container_op
        def echo_podname():
            import os

            print(os.environ.get("POD_NAME"))


        @kfp.dsl.pipeline()
        def simple_pipeline():
            op = echo_podname()
            op.apply(kfxutils.set_pod_metadata_envs())

    Args:
        pod_name (str, optional): Env var name for the pod name.
            Defaults to "POD_NAME".
        namespace (str, optional): Env var name for the namespace.
            Defaults to "NAMESPACE".
        node_name (str, optional): Env var name for the node name.
            Defaults to "NODE_NAME".

    Returns:
        Callable[[kfp.dsl.ContainerOp], kfp.dsl.ContainerOp]: kfp op.
    """

    def apply_pod_metadata_envs(task: kfp.dsl.ContainerOp) -> kfp.dsl.ContainerOp:
        for name, field_path in [
            (pod_name, "metadata.name"),
            (namespace, "metadata.namespace"),
            (node_name, "spec.nodeName"),
        ]:

            task.container.add_env_variable(
                k8s_client.V1EnvVar(
                    name=name,
                    value_from=k8s_client.V1EnvVarSource(
                        field_ref=k8s_client.V1ObjectFieldSelector(
                            field_path=field_path
                        )
                    ),
                )
            )
        return task

    return apply_pod_metadata_envs


# https://github.com/argoproj/argo/blob/51cdf95b18c8532f0bdb72c7ca20d56bdafc3a60/docs/workflow-controller-configmap.yaml
class ArtifactLocationHelper:
    """Helper class to generate artifact location from argo configs.

    Example::


        helper = kfxutils.ArtifactLocationHelper(
            scheme="minio", bucket="mlpipeline", key_prefix="artifacts/"
        )

        @kfp.components.func_to_container_op
        def test_op(
            mlpipeline_ui_metadata: OutputTextFile(str),
            markdown_file: OutputTextFile(str),
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
    """

    artifact_loc_env: str = "WORKFLOW_ARTIFACT_LOCATION"
    artifact_prefix_env: str = "WORKFLOW_ARTIFACT_PREFIX"

    def __init__(
        self, scheme: str, bucket: str, key_prefix: str = "", key_format: str = ""
    ):
        """Creates a new instance of ArtifactLocationHelper object.

        Args:
            scheme (str): Storage scheme, e.g. s3, minio, gcs.
            bucket (str): Name of the bucket.
            key_prefix (str, optional): Key prefix set inside argo artifactory
                configmap. Will not be used if key_format is provided.
                Defaults to "".
            key_format (str, optional): Key format set inside argo artifactory
                configmap. Defaults to "".
        """

        self.scheme = scheme
        self.bucket = bucket
        self.key_prefix = key_prefix
        self.key_format = key_format

    # ref
    # https://github.com/argoproj/argo/blob/f25a45deb4a7179044034da890884432e750d98a/workflow/controller/workflowpod.go#L859
    # artifact location is defaulted using the following formula:
    #   <worflow_name>/<pod_name>/<artifact_name>.tgz
    #   (e.g. myworkflowartifacts/argo-wf-fhljp/argo-wf-fhljp-123291312382/src.tgz)
    def get_artifact_location(self) -> str:
        """Returns the path to the artifact location.

        Returns:
            str: path to the artifact location.
        """
        if self.key_format:
            return os.path.join(self.bucket, self.key_format)

        return os.path.join(self.bucket, self.key_prefix, DEFAULT_KEY_FORMAT)

    def set_envs(
        self, image: str = "e2fyi/kfx:latest"
    ) -> Callable[[kfp.dsl.ContainerOp], kfp.dsl.ContainerOp]:
        """A kfp task modifier.

        This task modifier appends 2 env variables to the task, which
        can be subsequently used to determine the artifact location and prefix.

        Args:
            image (str, optional): image to use for the task. Defaults to
                "e2fyi/kfx:latest".

        Returns:
            Callable[[kfp.dsl.ContainerOp], kfp.dsl.ContainerOp]: modified task.
        """

        def mod1(task: kfp.dsl.ContainerOp):
            task.container.image = image
            artifact_prefix = _kfp_k8s_helper.sanitize_k8s_name(task.name)
            return set_workflow_env(
                WorkflowVars(name=self.artifact_prefix_env, template=artifact_prefix)
            )(task)

        mod2 = set_workflow_env(
            WorkflowVars(
                name=self.artifact_loc_env,
                template="%s://%s" % (self.scheme, self.get_artifact_location()),
            )
        )
        return lambda task: mod2(mod1(task))


def get_artifact_uri(name: str, ext: str = ".tgz") -> str:
    """This function should be used inside the kfp task to get the artifact.

    uri, which then can be provided to the kubeflow pipeline UI - i.e. as the
    `source` field inside kubeflow pipeline ui metadata.

    NOTE
    Artifact name with '_file' or '_path' will be removed.

    See
    https://github.com/kubeflow/pipelines/blob/4cb81ea047361ddce7ce8b0b68133b0a92724588/sdk/python/kfp/components/_python_op.py#L322

    Example::

        @kfp.components.func_to_container_op
        def test_op(
            mlpipeline_ui_metadata: OutputTextFile(str),
            markdown_file: OutputTextFile(str),
        ):

            import kfx.lib.utils as kfxutils
            import kfx.lib.vis as kfxvis

            markdown_file.write("### hello world")
            ui_metadata = kfxvis.kfp_ui_metadata(
                # markdown_file -> markdown
                [kfxvis.markdown(kfxutils.get_artifact_uri("markdown"))]
            )

            # mlpipeline_ui_metadata -> mlpipeline-ui-metadata
            mlpipeline_ui_metadata.write(kfxvis.asjson(ui_metadata))

            print(ui_metadata.outputs[0].source)


    Args:
        name (str): name of the artifact.
        ext (str, optional): extension for the artifact. Defaults to ".tgz".

    Returns:
        str: uri to the artifact which can be provided to kfp ui.
    """
    # sanitize_k8s_name
    artifact_loc = os.environ[ArtifactLocationHelper.artifact_loc_env]
    artifact_prefix = os.environ[ArtifactLocationHelper.artifact_prefix_env]
    return os.path.join(artifact_loc, "%s-%s%s" % (artifact_prefix, name, ext))
