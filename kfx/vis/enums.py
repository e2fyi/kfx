"""Enums used for kfx.vis."""
from enum import Enum


class KfpVisType(str, Enum):
    """Types of visualization available inside kubeflow pipeline UI."""

    confusion_matrix = "confusion_matrix"
    markdown = "markdown"
    roc = "roc"
    table = "table"
    tensorboard = "tensorboard"
    web_app = "web-app"


class KfpArtifactDataFormat(str, Enum):
    """Supported data format for kubeflow pipeline data artifact for visualization."""

    csv = "csv"


class KfpDataType(str, Enum):
    """Supported data type for data column inside a kubeflow pipeline artifact."""

    CATEGORY = "CATEGORY"
    NUMBER = "NUMBER"
    KEY = "KEY"
    TEXT = "TEXT"
    IMAGE_URL = "IMAGE_URL"


class KfpStorage(str, Enum):
    """Storage medium for visualization source."""

    inline = "inline"
    gcs = "gcs"
    minio = "minio"
    s3 = "s3"
    http = "http"
    https = "https"


class KfpMetricFormat(str, Enum):
    """Metric format."""

    PERCENTAGE = "PERCENTAGE"
    RAW = "RAW"
