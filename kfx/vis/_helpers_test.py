"""Tests for kfx.lib.vis."""
import kfx.vis._helpers as kfxvis


def test_confusion_matrix():
    expected = {
        "type": "confusion_matrix",
        "format": "csv",
        "schema": [
            {"name": "target", "type": "CATEGORY"},
            {"name": "predicted", "type": "CATEGORY"},
            {"name": "count", "type": "NUMBER"},
        ],
        "source": "gs://your_project/your_bucket/your_cm_file",
        "labels": ["True", "False"],
    }
    data = kfxvis.confusion_matrix(
        source="gs://your_project/your_bucket/your_cm_file", labels=["True", "False"]
    )
    assert kfxvis.asdict(data) == expected, "generates json for confusion matrix"


def test_markdown_inline():
    expected = {
        "storage": "inline",
        "source": "# Inline Markdown\n[A link](https://www.kubeflow.org/)",
        "type": "markdown",
    }
    data = kfxvis.markdown(
        "# Inline Markdown\n[A link](https://www.kubeflow.org/)", storage="inline"
    )
    assert kfxvis.asdict(data) == expected, "generates json for inline markdown"


def test_markdown_file():
    expected = {
        "source": "gs://your_project/your_bucket/your_markdown_file",
        "type": "markdown",
    }
    data = kfxvis.markdown("gs://your_project/your_bucket/your_markdown_file")
    assert kfxvis.asdict(data) == expected, "generates json for file-based markdown"


def test_roc():
    expected = {
        "type": "roc",
        "format": "csv",
        "schema": [
            {"name": "fpr", "type": "NUMBER"},
            {"name": "tpr", "type": "NUMBER"},
            {"name": "thresholds", "type": "NUMBER"},
        ],
        "source": "gs://your_project/your_bucket/your_roc_file",
    }
    data = kfxvis.roc("gs://your_project/your_bucket/your_roc_file")
    assert kfxvis.asdict(data) == expected, "generates json for roc"


def test_table():
    expected = {
        "type": "table",
        "storage": "gcs",
        "format": "csv",
        "header": ["col1", "col2"],
        "source": "gs://your_project/your_bucket/your_csv_file",
    }
    data = kfxvis.table(
        "gs://your_project/your_bucket/your_csv_file",
        header=["col1", "col2"],
        storage="gcs",
    )
    assert kfxvis.asdict(data) == expected, "generates json for table"


def test_tensorboard():
    expected = {"type": "tensorboard", "source": "gs://your_project/your_bucket/logs/*"}
    data = kfxvis.tensorboard("gs://your_project/your_bucket/logs/*")
    assert kfxvis.asdict(data) == expected, "generates json for tensorboard"


def test_webapp():
    expected = {
        "type": "web-app",
        "source": "gs://your_project/your_bucket/your_html_file",
        "storage": "gcs",
    }
    data = kfxvis.web_app("gs://your_project/your_bucket/your_html_file", storage="gcs")
    assert kfxvis.asdict(data) == expected, "generates json for web app"


def test_ui_metadata():
    expected = {
        "version": 1,
        "outputs": [
            {
                "type": "confusion_matrix",
                "format": "csv",
                "schema": [
                    {"name": "target", "type": "CATEGORY"},
                    {"name": "predicted", "type": "CATEGORY"},
                    {"name": "count", "type": "NUMBER"},
                ],
                "source": "gs://your_project/your_bucket/your_cm_file",
                "labels": ["True", "False"],
            },
            {
                "storage": "inline",
                "source": "# Inline Markdown\n[A link](https://www.kubeflow.org/)",
                "type": "markdown",
            },
            {
                "source": "gs://your_project/your_bucket/your_markdown_file",
                "type": "markdown",
            },
            {
                "type": "roc",
                "format": "csv",
                "schema": [
                    {"name": "fpr", "type": "NUMBER"},
                    {"name": "tpr", "type": "NUMBER"},
                    {"name": "thresholds", "type": "NUMBER"},
                ],
                "source": "gs://your_project/your_bucket/your_roc_file",
            },
            {
                "type": "table",
                "storage": "gcs",
                "format": "csv",
                "header": ["col1", "col2"],
                "source": "gs://your_project/your_bucket/your_csv_file",
            },
            {"type": "tensorboard", "source": "gs://your_project/your_bucket/logs/*"},
            {
                "type": "web-app",
                "source": "gs://your_project/your_bucket/your_html_file",
                "storage": "gcs",
            },
        ],
    }
    data = kfxvis.kfp_ui_metadata(
        [
            kfxvis.confusion_matrix(
                source="gs://your_project/your_bucket/your_cm_file",
                labels=["True", "False"],
            ),
            kfxvis.markdown(
                "# Inline Markdown\n[A link](https://www.kubeflow.org/)",
                storage="inline",
            ),
            kfxvis.markdown("gs://your_project/your_bucket/your_markdown_file"),
            kfxvis.roc("gs://your_project/your_bucket/your_roc_file"),
            kfxvis.table(
                "gs://your_project/your_bucket/your_csv_file",
                header=["col1", "col2"],
                storage="gcs",
            ),
            kfxvis.tensorboard("gs://your_project/your_bucket/logs/*"),
            kfxvis.web_app(
                "gs://your_project/your_bucket/your_html_file", storage="gcs"
            ),
        ]
    )
    assert kfxvis.asdict(data) == expected, "generates json for kfp ui metadata"
