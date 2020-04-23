"""Test for ContainerOp transformers."""
import pytest
import kfp.dsl

from kfx.dsl._transformers import ContainerOpTransform


@pytest.fixture
def op() -> kfp.dsl.ContainerOp:
    return kfp.dsl.ContainerOp(
        name="hello",
        image="bash",
        sidecars=[
            kfp.dsl.Sidecar(name="foo", image="bash"),
            kfp.dsl.Sidecar(name="bar", image="bash"),
        ],
    )


def test_containerop_transform_image_pull_policy(op: kfp.dsl.ContainerOp):

    transform = (
        ContainerOpTransform()
        .set_image_pull_policy("Always")
        .set_sidecar_image_pull_policy("Always", "f*")
    )

    op.apply(transform)
    assert op.container.image_pull_policy == "Always"
    assert [sidecar.image_pull_policy for sidecar in op.sidecars] == ["Always", None]


def test_containerop_transform_set_resources(op: kfp.dsl.ContainerOp):
    transform = ContainerOpTransform().set_resources(cpu=(1, 2), memory=("1G", "2G"))
    op.apply(transform)
    assert op.container.resources.requests == {"cpu": "1", "memory": "1G"}
    assert op.container.resources.limits == {"cpu": "2", "memory": "2G"}

    transform = ContainerOpTransform().set_resources(cpu="500m", memory="4G")
    op.apply(transform)
    assert op.container.resources.requests == {"cpu": "500m", "memory": "4G"}
    assert op.container.resources.limits == {"cpu": "500m", "memory": "4G"}


def test_containerop_transform_set_sidecar_resources(op: kfp.dsl.ContainerOp):

    transform = ContainerOpTransform().set_sidecar_resources(cpu="500m", memory="4G")
    op.apply(transform)
    assert [sidecar.resources.requests for sidecar in op.sidecars] == [
        {"cpu": "500m", "memory": "4G"},
        {"cpu": "500m", "memory": "4G"},
    ]
    assert [sidecar.resources.limits for sidecar in op.sidecars] == [
        {"cpu": "500m", "memory": "4G"},
        {"cpu": "500m", "memory": "4G"},
    ]

    transform = (
        ContainerOpTransform()
        .set_sidecar_resources(cpu=(1, 2), memory=("1G", "2G"), sidecar_name="f*")
        .set_sidecar_resources(cpu="200m", memory="3G", sidecar_name="bar")
    )
    op.apply(transform)
    assert [sidecar.resources.requests for sidecar in op.sidecars] == [
        {"cpu": "1", "memory": "1G"},
        {"cpu": "200m", "memory": "3G"},
    ]
    assert [sidecar.resources.limits for sidecar in op.sidecars] == [
        {"cpu": "2", "memory": "2G"},
        {"cpu": "200m", "memory": "3G"},
    ]


def test_containerop_transform_set_annotation_labels(op: kfp.dsl.ContainerOp):
    transform = (
        ContainerOpTransform()
        .set_annotations({"foo": "bar"})
        .set_labels({"hello": "world"})
    )
    op.apply(transform)

    assert op.pod_annotations == {"foo": "bar"}
    assert op.pod_labels == {"hello": "world"}


def test_containerop_transform_add_envs(op: kfp.dsl.ContainerOp):
    transform = (
        ContainerOpTransform()
        .add_env_var("foo", "bar")
        .add_env_vars({"hello": "world"})
        .add_env_var_from_secret(
            "creds", secret_name="k8s_secret", secret_key="access_key"
        )
        .add_env_var_from_configmap("some_configmap")
    )
    op.apply(transform)

    assert [obj.to_dict() for obj in op.container.env] == [
        {"name": "foo", "value": "bar", "value_from": None},
        {"name": "hello", "value": "world", "value_from": None},
        {
            "name": "creds",
            "value": None,
            "value_from": {
                "config_map_key_ref": None,
                "field_ref": None,
                "resource_field_ref": None,
                "secret_key_ref": {
                    "key": "access_key",
                    "name": "k8s_secret",
                    "optional": None,
                },
            },
        },
    ]

    assert [obj.to_dict() for obj in op.container.env_from] == [
        {
            "config_map_ref": {"name": "some_configmap", "optional": None},
            "prefix": None,
            "secret_ref": None,
        }
    ]
