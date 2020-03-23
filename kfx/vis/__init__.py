"""Extensions for visualizations in kubeflow.

::

    import kfp.components
    import kfx.vis

    from kfx.vis.enums import KfpStorage, KfpMetricFormat


    @func_to_container_op
    def some_op(
        mlpipeline_ui_metadata: OutputTextFile(str), mlpipeline_metrics: OutputTextFile(str)
    ):
        "kfp operator that provides metadata for visualizations."

        ui_metadata = kfx.vis.kfp_ui_metadata(
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
                # creates a Vega-Lite vis as a web app
                kfx.vis.vega_web_app(spec={
                    "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
                    "description": "A simple bar chart with embedded data.",
                    "data": {
                        "values": [
                            {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43},
                            {"a": "D", "b": 91}, {"a": "E", "b": 81}, {"a": "F", "b": 53},
                            {"a": "G", "b": 19}, {"a": "H", "b": 87}, {"a": "I", "b": 52}
                        ]
                    },
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "a", "type": "ordinal"},
                        "y": {"field": "b", "type": "quantitative"}
                    }
                })
            ]
        )

        # write ui metadata so that kubeflow pipelines UI can render visualizations
        mlpipeline_ui_metadata.write(kfx.vis.asjson(ui_metadata))


        # create metrics
        metrics = kfp_metrics([
            # override metric format with custom value
            kfp_metric(name="accuracy-score", value=0.8, metric_format="PERCENTAGE"),
            # render recall as percent
            kfp_metric("recall-score", 0.9, percent=true),
            # raw score
            kfp_metric("raw-score", 123.45),
        ])

        # write metrics to kubeflow pipelines UI
        mlpipeline_metrics.write(kfx.vis.asjson(metrics))

"""
from kfx.vis._helpers import (
    roc,
    table,
    asdict,
    asjson,
    web_app,
    markdown,
    kfp_metric,
    kfp_metrics,
    tensorboard,
    tolocalfile,
    kfp_ui_metadata,
    confusion_matrix,
)
