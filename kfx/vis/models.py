"""Data models for generating visualization in Kubeflow pipelines UI."""
from typing import Any, List, Union, Optional

from pydantic import Field, BaseModel

from kfx.vis.enums import (
    KfpStorage,
    KfpVisType,
    KfpDataType,
    KfpMetricFormat,
    KfpArtifactDataFormat,
)


def _write_to(datamodel: BaseModel, obj: Any):
    """Write json string of a data model to a `kfp.components.OutputPath` or `kfp.components.OutputTextFile` obj.

    Args:
        datamodel (BaseModel): pydantic model object.
        obj (Any): `kfp.components.OutputPath` or `kfp.components.OutputTextFile`
    """
    if hasattr(obj, "write"):
        obj.write(datamodel.json(exclude_none=True, by_alias=True))
    else:
        with open(str(obj), "w") as writer:
            writer.write(datamodel.json(exclude_none=True, by_alias=True))


class KfpArtifactSchema(BaseModel):
    """Schema for columnar data inside a kubeflow pipeline artifact."""

    name: str
    type: KfpDataType


class KfpVis(BaseModel):
    """Parameters to generate a visualization inside kubeflow pipeline UI."""

    artifact_format: Optional[KfpArtifactDataFormat] = Field(
        None,
        alias="format",
        description="The format of the artifact data. The default is `csv`. "
        "Note: The only format currently available is `csv`.",
    )
    header: Optional[List[str]] = Field(
        None,
        description="A list of strings to be used as headers for the artifact data. "
        "For example, in a table these strings are used in the first row.",
    )
    labels: Optional[List[str]] = Field(
        None,
        description="A list of strings to be used as labels for artifact columns or "
        "rows.",
    )
    predicted_col: Optional[str] = Field(
        None, description="Name of the predicted column."
    )
    artifact_schema: Optional[List[KfpArtifactSchema]] = Field(  # type: ignore
        None,
        alias="schema",
        description="A list of `{type, name}` objects that specify the schema of the "
        "artifact data.",
    )
    source: Optional[str] = Field(
        None,
        description="The full path to the data. The available locations include "
        "`http`, `https`, `Amazon S3`, `Minio`, and `Google Cloud Storage`. "
        "The path can contain wildcards `*`, in which case the Kubeflow Pipelines "
        "UI concatenates the data from the matching source files. "
        "For some viewers, this field can contain inlined string data instead of a "
        "path.",
    )
    storage: Optional[KfpStorage] = Field(
        None,
        description="Applies only to outputs of type `markdown`. "
        "Set to `inline` if `source` contains the actual markdown instead of a "
        "remote source.",
    )
    target_col: Optional[str] = Field(None, description="Name of the target column.")
    type: KfpVisType = Field(
        None,
        description="Types of visualization. "
        "e.g. confustion_matrix, markdown, roc, table, tensorboard, or web-app.",
    )

    class Config:
        """Config model to use alias as schema is a protected key for pydantic."""

        allow_population_by_field_name = True


class ConfusionMatrix(KfpVis):
    """Visualizes a confusion matrix.

    The confusion_matrix viewer plots a confusion matrix visualization
    of the data from the given source path, using the schema to parse
    the data. The labels provide the names of the classes to be plotted
    on the x and y axes.
    """

    type: KfpVisType = Field(
        KfpVisType.confusion_matrix,
        const=True,
        description="Types of visualization. "
        "e.g. confustion_matrix, markdown, roc, table, tensorboard, or web-app.",
    )
    source: str = Field(
        ...,
        description="The full path to the data. The available locations include "
        "`http`, `https`, `Amazon S3`, `Minio`, and `Google Cloud Storage`. "
        "The path can contain wildcards `*`, in which case the Kubeflow Pipelines "
        "UI concatenates the data from the matching source files. "
        "For some viewers, this field can contain inlined string data instead of a "
        "path.",
    )
    artifact_format: KfpArtifactDataFormat = Field(
        KfpArtifactDataFormat.csv,
        alias="format",
        description="The format of the artifact data. The default is `csv`. "
        "Note: The only format currently available is `csv`.",
    )
    artifact_schema: List[KfpArtifactSchema] = Field(  # type: ignore
        [
            {"name": "target", "type": "CATEGORY"},
            {"name": "predicted", "type": "CATEGORY"},
            {"name": "count", "type": "NUMBER"},
        ],
        alias="schema",
        description="A list of `{type, name}` objects that specify the schema of the "
        "artifact data.",
    )
    labels: List[str] = Field(
        ...,
        description="A list of strings to be used as labels for artifact columns or "
        "rows.",
    )


class Markdown(KfpVis):
    """Visualizes a markdown.

    The markdown viewer renders Markdown strings on the Kubeflow Pipelines UI.
    The viewer can read the Markdown data from the following locations:

    -   A Markdown-formatted string embedded in the source field. The value of the
        storage field must be `inline`.

    -   Markdown code in a remote file, at a path specified in the source field.
        The storage field can contain any value except `inline`.
    """

    type: KfpVisType = Field(
        KfpVisType.markdown,
        const=True,
        description="Types of visualization. "
        "e.g. confustion_matrix, markdown, roc, table, tensorboard, or web-app.",
    )
    source: str = Field(
        ...,
        description="The full path to the data. The available locations include "
        "`http`, `https`, `Amazon S3`, `Minio`, and `Google Cloud Storage`. "
        "The path can contain wildcards `*`, in which case the Kubeflow Pipelines "
        "UI concatenates the data from the matching source files. "
        "For some viewers, this field can contain inlined string data instead of a "
        "path.",
    )
    storage: Optional[KfpStorage] = Field(
        None,
        description="Applies only to outputs of type `markdown`. "
        "Set to `inline` if `source` contains the actual markdown instead of a "
        "remote source.",
    )


class Roc(KfpVis):
    """Visualizes a ROC curve.

    The roc viewer plots a receiver operating characteristic (ROC) curve using the
    data from the given source path. The Kubeflow Pipelines UI assumes that the schema
    includes three columns with the following names:

    - fpr (false positive rate)
    - tpr (true positive rate)
    - thresholds

    When viewing the ROC curve, you can hover your cursor over the ROC curve to see
    the threshold value used for the cursor’s closest fpr and tpr values.
    """

    type: KfpVisType = Field(
        KfpVisType.roc,
        const=True,
        description="Types of visualization. "
        "e.g. confustion_matrix, markdown, roc, table, tensorboard, or web-app.",
    )
    artifact_format: KfpArtifactDataFormat = Field(
        KfpArtifactDataFormat.csv,
        alias="format",
        description="The format of the artifact data. The default is `csv`. "
        "Note: The only format currently available is `csv`.",
    )
    artifact_schema: List[KfpArtifactSchema] = Field(  # type: ignore
        [
            {"name": "fpr", "type": "NUMBER"},
            {"name": "tpr", "type": "NUMBER"},
            {"name": "thresholds", "type": "NUMBER"},
        ],
        alias="schema",
        description="A list of `{type, name}` objects that specify the schema of the "
        "artifact data.",
    )
    source: str = Field(
        ...,
        description="The full path to the data. The available locations include "
        "`http`, `https`, `Amazon S3`, `Minio`, and `Google Cloud Storage`. "
        "The path can contain wildcards `*`, in which case the Kubeflow Pipelines "
        "UI concatenates the data from the matching source files. "
        "For some viewers, this field can contain inlined string data instead of a "
        "path.",
    )


class Table(KfpVis):
    """Visualizes a table.

    The table viewer builds an HTML table out of the data at the given source path,
    where the header field specifies the values to be shown in the first row of the
    table.

    The table supports pagination.
    """

    type: KfpVisType = Field(
        KfpVisType.table,
        const=True,
        description="Types of visualization. "
        "e.g. confustion_matrix, markdown, roc, table, tensorboard, or web-app.",
    )
    artifact_format: KfpArtifactDataFormat = Field(
        KfpArtifactDataFormat.csv,
        alias="format",
        description="The format of the artifact data. The default is `csv`. "
        "Note: The only format currently available is `csv`.",
    )
    header: List[str] = Field(
        ...,
        description="A list of strings to be used as headers for the artifact data. "
        "For example, in a table these strings are used in the first row.",
    )
    source: str = Field(
        ...,
        description="The full path to the data. The available locations include "
        "`http`, `https`, `Amazon S3`, `Minio`, and `Google Cloud Storage`. "
        "The path can contain wildcards `*`, in which case the Kubeflow Pipelines "
        "UI concatenates the data from the matching source files. "
        "For some viewers, this field can contain inlined string data instead of a "
        "path.",
    )


class Tensorboard(KfpVis):
    """Provides a tensorboard viewer.

    The tensorboard viewer adds a Start Tensorboard button to the output page.

    When viewing the output page, you can:

    -   Click Start Tensorboard to start a TensorBoard Pod in your Kubeflow cluster.
        The button text switches to Open Tensorboard.

    -   Click Open Tensorboard to open the TensorBoard interface in a new tab,
        pointing to the logdir data specified in the source field.

    Note:
    The Kubeflow Pipelines UI doesn’t fully manage your TensorBoard instances.
    The “Start Tensorboard” button is a convenience feature so that you don’t have
    to interrupt your workflow when looking at pipeline runs. You’re responsible
    for recycling or deleting the TensorBoard Pods using your Kubernetes management
    tools.
    """

    type: KfpVisType = Field(
        KfpVisType.tensorboard,
        const=True,
        description="Types of visualization. "
        "e.g. confustion_matrix, markdown, roc, table, tensorboard, or web-app.",
    )
    source: str = Field(
        ...,
        description="The full path to the data. The available locations include "
        "`http`, `https`, `Amazon S3`, `Minio`, and `Google Cloud Storage`. "
        "The path can contain wildcards `*`, in which case the Kubeflow Pipelines "
        "UI concatenates the data from the matching source files. "
        "For some viewers, this field can contain inlined string data instead of a "
        "path.",
    )


class WebApp(KfpVis):
    """Provides a web-app viewer.

    The web-app viewer provides flexibility for rendering custom output.
    You can specify an HTML file that your component creates, and the
    Kubeflow Pipelines UI renders that HTML in the output page. The HTML
    file must be self-contained, with no references to other files in
    the filesystem. The HTML file can contain absolute references to
    files on the web. Content running inside the web app is isolated in
    an iframe and cannot communicate with the Kubeflow Pipelines UI.
    """

    type: KfpVisType = Field(
        KfpVisType.web_app,
        const=True,
        description="Types of visualization. "
        "e.g. confustion_matrix, markdown, roc, table, tensorboard, or web-app.",
    )
    source: str = Field(
        ...,
        description="The full path to the data. The available locations include "
        "`http`, `https`, `Amazon S3`, `Minio`, and `Google Cloud Storage`. "
        "The path can contain wildcards `*`, in which case the Kubeflow Pipelines "
        "UI concatenates the data from the matching source files. "
        "For some viewers, this field can contain inlined string data instead of a "
        "path.",
    )


class KfpUiMetadata(BaseModel):
    """Describes the visualization to render inside kubeflow pipeline UI."""

    version: Union[int, str] = Field(
        1, description="Version of the kubeflow pipeline ui metadata schema."
    )
    outputs: List[
        Union[ConfusionMatrix, Roc, Markdown, Table, Tensorboard, WebApp]
    ] = Field(
        [], description="List of objects describing the desired kfp visualizations."
    )

    def write_to(self, obj: Any):
        """Writes kubeflow metrics object to a path or a File-like object.

        Args:
            obj (Any): Path or File-like object.
        """
        _write_to(self, obj)


class KfpMetric(BaseModel):
    """Describes a single metric from a kubeflow pipeline task."""

    name: str = Field(
        ...,
        description="Name of the metric. Must be format: ^[a-z]([-a-z0-9]{0,62}[a-z0-9])?$",
    )
    numberValue: Union[float, int] = Field(
        ..., description="Numerical value of the metric."
    )
    format: Optional[KfpMetricFormat] = Field(
        None, description="can only be PERCENTAGE, RAW, or not set"
    )


class KfpMetrics(BaseModel):
    """Describes the metrics outputs of a kubeflow pipeline task."""

    metrics: List[KfpMetric] = Field([], description="A list of KfpMetric objects.")

    def write_to(self, obj: Any):
        """Writes kubeflow metrics object to a path or a File-like object.

        Args:
            obj (Any): Path or File-like object.
        """
        _write_to(self, obj)
