"""Extensions for visualizations in kubeflow.

::

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

"""
from kfx.vis._helpers import (
    roc,
    table,
    asdict,
    asjson,
    web_app,
    markdown,
    tensorboard,
    tolocalfile,
    kfp_ui_metadata,
    confusion_matrix,
)
