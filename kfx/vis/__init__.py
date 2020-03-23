"""Extensions for visualizations in kubeflow.

::

    import functools

    import kfp.components


    # install kfx
    kfx_component = functools.partial(kfp.components.func_to_container_op, packages_to_install=["kfx"])


    @kfx_component
    def some_op(
        # mlpipeline_metrics is a path - i.e. open(mlpipeline_metrics, "w")
        mlpipeline_metrics: kfp.components.OutputPath(str),
        # mlpipeline_ui_metadata is a FileLike obj - i.e. mlpipeline_ui_metadata.write("something")
        mlpipeline_ui_metadata: kfp.components.OutputTextFile(str),
    ):
        "kfp operator that provides metrics and metadata for visualizations."

        # import inside kfp task
        import kfx.vis

        # output metrics to mlpipeline_metrics path
        kfx.vis.kfp_metrics([
            # render as percent
            kfx.vis.kfp_metric("recall-score", 0.9, percent=true),
            # override metric format with custom value
            kfx.vis.kfp_metric(name="percision-score", value=0.8, metric_format="PERCENTAGE"),
            # render raw score
            kfx.vis.kfp_metric("raw-score", 123.45),
        ]).write_to(mlpipeline_metrics)

        # output visualization metadata to mlpipeline_ui_metadata obj
        kfx.vis.kfp_ui_metadata(
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
        ).write_to(mlpipeline_ui_metadata)


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
