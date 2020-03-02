"""Helper functions for generating visualization in Kubeflow pipelines UI."""
from typing import List, Union, Optional

from pydantic import BaseModel

from kfx.dsl import KfpArtifact
from kfx.vis.models import (
    Roc,
    Table,
    WebApp,
    Markdown,
    KfpStorage,
    Tensorboard,
    KfpUiMetadata,
    ConfusionMatrix,
    KfpArtifactDataFormat,
)

KFP_UI_METADATA_PATH = "/mlpipeline-ui-metadata.json"


def confusion_matrix(
    source: Union[str, KfpArtifact],
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
        source (Union[str, KfpArtifact]): Full path to the data artifact.
        labels (List[str]): Names of the classes to be plotted on the x and y axes.
        artifact_format (Union[KfpArtifactDataFormat, str], optional):
            Data format for the artifact. Defaults to "csv".

    Returns:
        ConfusionMatrix: pydantic data object.
    """
    return ConfusionMatrix(
        source=str(source), artifact_format=artifact_format, labels=labels, **kwargs
    )


def markdown(
    source: Union[str, KfpArtifact],
    storage: Optional[Union[KfpStorage, str]] = None,
    **kwargs,
) -> Markdown:
    """Helper function to create a KfpUiMetadata Markdown object.

    Args:
        source (Union[str, KfpArtifact]): Full path to the markdown or the actual markdown
            text.
        storage (Optional[Union[KfpStorage, str]], optional): Set "inline"
            if source has the actual markdown text. Defaults to None.

    Returns:
        Markdown: pydantic data object.
    """
    return Markdown(source=str(source), storage=storage, **kwargs)


def roc(
    source: Union[str, KfpArtifact],
    artifact_format: Union[KfpArtifactDataFormat, str] = "csv",
    **kwargs,
) -> Roc:
    """Helper function to create a KfpUiMetadata Roc object.

    The source artifact must be a CSV with the following 3 columns:
    - fpr (false positive rate)
    - tpr (true positive rate)
    - thresholds

    Args:
        source (Union[str, KfpArtifact]): Full path to roc data.
        artifact_format (Union[KfpArtifactDataFormat, str], optional):
            Data format for the artifact. Defaults to "csv".

    Returns:
        Roc: pydantic data object.
    """
    return Roc(source=str(source), artifact_format=artifact_format, **kwargs)


def table(
    source: Union[str, KfpArtifact],
    header: List[str],
    artifact_format: Union[KfpArtifactDataFormat, str] = "csv",
    **kwargs,
) -> Table:
    """Helper function to create a KfpUiMetadata Table object.

    Args:
        source (Union[str, KfpArtifact]): Full path to the data.
        header (List[str]): Headers to use for the table.
        artifact_format (Union[KfpArtifactDataFormat, str], optional):
            Data format for the artifact. Defaults to "csv".

    Returns:
        Table: pydantic data object.
    """
    return Table(
        source=str(source), header=header, artifact_format=artifact_format, **kwargs
    )


def tensorboard(source: Union[str, KfpArtifact], **kwargs) -> Tensorboard:
    """Helper function to create a KfpUiMetadata Tensorboard object.

    Args:
        source (Union[str, KfpArtifact]): The full path to the tensorboard logs. Supports * wildcards.

    Returns:
        Tensorboard: pydantic data object.
    """
    return Tensorboard(source=str(source), **kwargs)


def web_app(source: Union[str, KfpArtifact], **kwargs) -> WebApp:
    """Helper function to create a KfpUiMetadata WebApp object.

    Args:
        source (Union[str, KfpArtifact]): The full path to the html content or inlined html.

    Returns:
        WebApp: pydantic data object.
    """

    return WebApp(source=str(source), **kwargs)


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
