"""Utils."""
import os
import os.path

from typing import Callable, NamedTuple

import kfp.dsl

from kubernetes import client as k8s_client

from kfx.dsl._compat import sanitize_k8s_name

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
    """Modifier for kubeflow pipelines tasks.

    Setup a kfp op to pass in the workflow variables as an environment var.

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

            # op will have an environment variable "WORKFLOW_NAME"
            # that provides the name of the workflow
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
    """Modifier for kubeflow pipelines tasks.

    Setup a kfp op to pass in the pod name, namespace, and node name as env
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


class ArtifactLocationHelper:
    """Helper class to generate artifact location based on provided argo config.

    See an example of an `Argo configmap <https://github.com/argoproj/argo/blob/master/docs/workflow-controller-configmap.yaml>`_.

    ::

        import kfp.components
        import kfp.dsl
        import kfx.dsl


        helper = kfx.dsl.ArtifactLocationHelper(
            scheme="minio", bucket="mlpipeline", key_prefix="artifacts/"
        )

        @kfp.components.func_to_container_op
        def test_op(
            mlpipeline_ui_metadata: OutputTextFile(str), markdown_data_file: OutputTextFile(str)
        ):
            "A test kubeflow pipeline task."

            import kfx.dsl
            import kfx.vis

            # write the markdown to the `markdown-data` artifact
            markdown_data_file.write("### hello world")

            # creates an ui metadata object
            ui_metadata = kfx.vis.kfp_ui_metadata(
                # Describes the vis to generate in the kubeflow pipeline UI.
                # In this case, a markdown vis from a markdown artifact.
                [kfx.vis.markdown(kfx.dsl.KfpArtifact("markdown_data_file"))]
                # `KfpArtifact` provides the reference to data artifact created
                # inside this task
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
    """

    artifact_prefix_env: str = "WORKFLOW_ARTIFACT_PREFIX"
    artifact_storage_env: str = "WORKFLOW_ARTIFACT_STORAGE"
    artifact_bucket_env: str = "WORKFLOW_ARTIFACT_BUCKET"
    artifact_key_prefix_env: str = "WORKFLOW_ARTIFACT_KEY_PREFIX"

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
    def _get_key_prefix(self) -> str:
        """Returns artifact key prefix.

        Returns:
            str: artifact key prefix
        """
        if self.key_format:
            return self.key_format

        return os.path.join(self.key_prefix, DEFAULT_KEY_FORMAT)

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

        def set_workflow_envs(task: kfp.dsl.ContainerOp):
            task.container.image = image
            artifact_prefix = sanitize_k8s_name(task.name)

            for name, value in [
                (self.artifact_storage_env, self.scheme),
                (self.artifact_bucket_env, self.bucket),
                (self.artifact_key_prefix_env, self._get_key_prefix()),
                (self.artifact_prefix_env, artifact_prefix),
            ]:
                task.container.add_env_variable(
                    k8s_client.V1EnvVar(name=name, value=value)
                )

        return set_workflow_envs


def _handle_special_artifact_names(name: str) -> str:
    """Always sanitize special artifact names (e.g. mlpipeline_ui_metadata)"""
    sanitized: str = sanitize_k8s_name(name)
    return (
        sanitized
        if sanitized in {"mlpipeline-ui-metadata", "mlpipeline-metrics"}
        else name
    )


def _sanitize_artifact_name(name: str, sanitize: bool = False) -> str:
    """Sanitize the artifact name based on k8s resource naming convention.

    Also remove suffixes "_path" and "_file". (See this `comment <https://github.com/kubeflow/pipelines/blob/4cb81ea047361ddce7ce8b0b68133b0a92724588/sdk/python/kfp/components/_python_op.py#L327>'_.)


    Args:
        name (str): [description]
        sanitize (bool, optional): Whether to sanitize the name. Defaults to False.

    Returns:
        str: [description]
    """
    if name.endswith("_path"):
        name = name[0 : -len("_path")]
    elif name.endswith("_file"):
        name = name[0 : -len("_file")]

    return (  # type: ignore
        sanitize_k8s_name(name) if sanitize else _handle_special_artifact_names(name)
    )


class KfpArtifact:
    """Class to represent a kubeflow pipeline artifact created inside the pipeline task."""

    def __init__(self, name: str, ext: str = ".tgz", sanitize_name: bool = False):
        """Reference to a kfp artifact that is created within the kubeflow pipeline task.

        This function should be used inside the kfp task. It returns the artifact uri,
        which then can be provided to the kubeflow pipeline UI - i.e. as the
        `source` field inside kubeflow pipeline ui metadata.

        ::

            import kfp.components
            import kfp.dsl
            import kfx.dsl


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

                # `KfpArtifact` provides the reference to data artifact created
                # inside this task
                spec = {
                    "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
                    "description": "A simple bar chart",
                    "data": {
                        "values": data,
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


        Args:
            name (str): name of the artifact.
            ext (str, optional): extension for the artifact. Defaults to ".tgz".
            sanitize_name (bool, optional): whether to sanitize the artifact name. Defaults to False.

        Returns:
            str: uri to the artifact which can be provided to kfp ui.
        """
        self.storage = os.environ[ArtifactLocationHelper.artifact_storage_env]
        self.bucket = os.environ[ArtifactLocationHelper.artifact_bucket_env]
        self.key_prefix = os.environ[ArtifactLocationHelper.artifact_key_prefix_env]
        self.prefix = os.environ[ArtifactLocationHelper.artifact_prefix_env]
        self.name = _sanitize_artifact_name(name, sanitize_name)
        self.ext = ext
        self.key = os.path.join(
            self.key_prefix, "%s-%s%s" % (self.prefix, self.name, self.ext)
        )

    @property
    def source(self) -> str:
        """Url to the artifact source."""
        path = os.path.join(self.bucket, self.key)
        return "%s://%s" % (self.storage, path)

    def __str__(self):
        """Url to the artifact source."""
        return self.source
