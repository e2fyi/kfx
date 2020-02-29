"""Data models and utils to generate kfp ui metadata for kubeflow pipelines."""
from enum import Enum
from typing import List, Union, Optional

from pydantic import Field, BaseModel

KFP_UI_METADATA_PATH = "/mlpipeline-ui-metadata.json"


class KfpVisType(str, Enum):
    """Types of visualization available inside kubeflow pipeline UI."""

    confusion_matrix = "confusion_matrix"
    markdown = "markdown"
    roc = "roc"
    table = "table"
    tensorboard = "tensorboard"
    web_app = "web-app"


class KfpArtifactDataFormat(str, Enum):
    """Supported data format for kubeflow pipeline data artifact for
    visualization."""

    csv = "csv"


class KfpDataType(str, Enum):
    """Supported data type for data column inside a kubeflow pipeline
    artifact."""

    CATEGORY = "CATEGORY"
    NUMBER = "NUMBER"
    KEY = "KEY"
    TEXT = "TEXT"
    IMAGE_URL = "IMAGE_URL"


class KfpArtifactSchema(BaseModel):
    """Schema for columnar data inside a kubeflow pipeline artifact."""

    name: str
    type: KfpDataType


class KfpStorage(str, Enum):
    """Storage medium for visualization source."""

    inline = "inline"
    gcs = "gcs"
    minio = "minio"
    s3 = "s3"
    http = "http"
    https = "https"


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
        """Config model to use alias as schema is a protected key for
        pydantic."""

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


def confusion_matrix(
    source: str,
    labels: List[str],
    artifact_format: Union[KfpArtifactDataFormat, str] = "csv",
    **kwargs,
) -> ConfusionMatrix:
    """Helper function to create a KfpUiMetadata ConfusionMatrix object.

    The source artifact must be a CSV with the following 3 columns:
    - target
    - predicted
    - count

    Args:
        source (str): Full path to the data artifact.
        labels (List[str]): Names of the classes to be plotted on the x and y axes.
        artifact_format (Union[KfpArtifactDataFormat, str], optional):
            Data format for the artifact. Defaults to "csv".

    Returns:
        ConfusionMatrix: pydantic data object.
    """
    return ConfusionMatrix(
        source=source, artifact_format=artifact_format, labels=labels, **kwargs
    )


def markdown(
    source: str, storage: Optional[Union[KfpStorage, str]] = None, **kwargs
) -> Markdown:
    """Helper function to create a KfpUiMetadata Markdown object.

    Args:
        source (str): Full path to the markdown or the actual markdown
            text.
        storage (Optional[Union[KfpStorage, str]], optional): Set "inline"
            if source has the actual markdown text. Defaults to None.

    Returns:
        Markdown: pydantic data object.
    """
    return Markdown(source=source, storage=storage, **kwargs)


def roc(
    source: str, artifact_format: Union[KfpArtifactDataFormat, str] = "csv", **kwargs
) -> Roc:
    """Helper function to create a KfpUiMetadata Roc object.

    The source artifact must be a CSV with the following 3 columns:
    - fpr (false positive rate)
    - tpr (true positive rate)
    - thresholds

    Args:
        source (str): Full path to roc data.
        artifact_format (Union[KfpArtifactDataFormat, str], optional):
            Data format for the artifact. Defaults to "csv".

    Returns:
        Roc: pydantic data object.
    """
    return Roc(source=source, artifact_format=artifact_format, **kwargs)


def table(
    source: str,
    header: List[str],
    artifact_format: Union[KfpArtifactDataFormat, str] = "csv",
    **kwargs,
) -> Table:
    """Helper function to create a KfpUiMetadata Table object.

    Args:
        source (str): Full path to the data.
        header (List[str]): Headers to use for the table.
        artifact_format (Union[KfpArtifactDataFormat, str], optional):
            Data format for the artifact. Defaults to "csv".

    Returns:
        Table: pydantic data object.
    """
    return Table(
        source=source, header=header, artifact_format=artifact_format, **kwargs
    )


def tensorboard(source: str, **kwargs) -> Tensorboard:
    """Helper function to create a KfpUiMetadata Tensorboard object.

    Args:
        source (str): The full path to the tensorboard logs. Supports * wildcards.

    Returns:
        Tensorboard: pydantic data object.
    """
    return Tensorboard(source=source, **kwargs)


def web_app(source: str, **kwargs) -> WebApp:
    """Helper function to create a KfpUiMetadata WebApp object.

    Args:
        source (str): The full path to the html content or inlined html.

    Returns:
        WebApp: pydantic data object.
    """
    return WebApp(source=source, **kwargs)


def kfp_ui_metadata(
    outputs: List[
        Union[ConfusionMatrix, Roc, Markdown, Table, Tensorboard, WebApp, dict]
    ],
    version: Union[int, str] = 1,
) -> KfpUiMetadata:
    """Helper function to create a KfpUiMetadata object.

    Args:
        outputs (List[Union[ConfusionMatrix, Roc, Markdown, Table, Tensorboard,
            WebApp, dict]]): List of KfpVis objects.
        version (Union[int, str], optional): Schema version. Defaults to 1.

    Returns:
        KfpUiMetadata: pydantic data object.
    """
    return KfpUiMetadata(version=version, outputs=outputs)


def asdict(obj: BaseModel) -> dict:
    """Returns the dict representations of the pydantic data object."""
    return obj.dict(exclude_none=True, by_alias=True)


def asjson(obj: BaseModel) -> str:
    """Return the JSON string representation of the pydantic data object."""
    return obj.json(exclude_none=True, by_alias=True)


def tolocalfile(obj: BaseModel, dst: str = KFP_UI_METADATA_PATH):
    """Writes a pydantic data object as a json file in local file system.

    Args:
        obj (BaseModel): pydantic data object.
        dst (str, optional): Destination path. Defaults to
            "/mlpipeline-ui-metadata.json".
    """
    with open(dst, "w") as fileout:
        fileout.write(asjson(obj))
