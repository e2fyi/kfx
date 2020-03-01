"""Extension to kfp dsl.

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
            [kfx.vis.markdown(kfx.dsl.kfp_artifact("markdown_data_file"))]
            # `kfp_artifact` provides the reference to data artifact created
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
from kfx.dsl._artifact_location import (
    WorkflowVars,
    ArtifactLocationHelper,
    kfp_artifact,
    set_workflow_env,
    set_pod_metadata_envs,
)
