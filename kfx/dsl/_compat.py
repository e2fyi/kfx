"""Module for compatibilities with potential updates in dependent packages."""
import re

from kfp.compiler._k8s_helper import sanitize_k8s_name as _sanitize_k8s_name


def __sanitize_k8s_name(name, allow_capital_underscore=False):
    """sanitize_k8s_name cleans and converts the names in the workflow.

    NOTE
    This is copied from the main kfp package which is from _make_kubernetes_name

    Args:
      name: original name,
      allow_capital_underscore: whether to allow capital letter and underscore
        in this name.

    Returns:
      sanitized name.
    """
    if allow_capital_underscore:
        return (
            re.sub("-+", "-", re.sub("[^-_0-9A-Za-z]+", "-", name))
            .lstrip("-")
            .rstrip("-")
        )
    return (
        re.sub("-+", "-", re.sub("[^-0-9a-z]+", "-", name.lower()))
        .lstrip("-")
        .rstrip("-")
    )


sanitize_k8s_name = (  # pylint: disable=invalid-name
    _sanitize_k8s_name or __sanitize_k8s_name
)
