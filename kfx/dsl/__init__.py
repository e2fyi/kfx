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

"""
from kfx.dsl._artifact_location import (
    KfpArtifact,
    WorkflowVars,
    ArtifactLocationHelper,
    set_workflow_env,
    set_pod_metadata_envs,
)
