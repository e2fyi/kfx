"""Transform functions that modify containerOp."""
from fnmatch import fnmatch
from typing import Callable, Dict, List, Tuple, Union

import kfp.dsl
import kubernetes.client as k8s

TransformFunc = Callable[[kfp.dsl.ContainerOp], kfp.dsl.ContainerOp]


class ContainerOpTransform:
    """Helper class to manipulate some common internal properties of ContainerOp.

    Please refer to documentation for full set of transforms available.

    ::

        import kfp.components
        import kfp.dsl
        import kfx.dsl

        transforms = (
            kfx.dsl.ContainerOpTransform()
            .set_resources(cpu="500m", memory=("1G", "4G"))
            .set_image_pull_policy("Always")
            .set_env_vars({"ENV": "production"})
            .set_env_var_from_secret("AWS_ACCESS_KEY", secret_name="aws", secret_key="access_key")
            .set_annotations({"iam.amazonaws.com/role": "some-arn"})
        )


        @kfp.dsl.components.func_to_container_op
        def echo(text: str) -> str:
            print(text)
            return text


        @kfp.dsl.pipeline(name="demo")
        def pipeline(text: str):
            op1 = echo(text)
            op2 = echo("%s-%s" % text)

            # u can apply the transform on op1 only
            # op1.apply(transforms)

            # or apply on all ops in the pipeline
            kfp.dsl.get_pipeline_conf().add_op_transformer(transforms)

    """

    def __init__(self, transforms: List[TransformFunc] = None):
        """Creates a new instance of ContainerOpTransform object.

        Args:
            transforms (List[TransformFunc], optional): Optional list of custom transform functions. Defaults to None.
        """
        self._transforms: List[TransformFunc] = transforms or []

    def __call__(self, op: kfp.dsl.ContainerOp) -> kfp.dsl.ContainerOp:
        """In-place transform of the provided ContainerOp.

        Args:
            op (kfp.dsl.ContainerOp): ContainerOp obj.

        Returns:
            kfp.dsl.ContainerOp: ContainerOp obj.
        """
        [  # pylint: disable=expression-not-assigned
            transform(op) for transform in self._transforms
        ]
        return op

    def set_annotations(self, annotations: Dict[str, str]) -> "ContainerOpTransform":
        """Update the transform function to set the provided annotations to the ContainerOp.

        Args:
            annotations (Dict[str, str]): dict of annotation keys and values.
        """

        def set_annotations_transform(op: kfp.dsl.ContainerOp) -> kfp.dsl.ContainerOp:
            [  # pylint: disable=expression-not-assigned
                op.add_pod_annotation(name, value)
                for name, value in annotations.items()
            ]
            return op

        self._transforms.append(set_annotations_transform)
        return self

    def set_labels(self, labels: Dict[str, str]) -> "ContainerOpTransform":
        """Update the transform function to set the provided labels to the ContainerOp.

        Args:
            labels (Dict[str, str]): dict of labels keys and values.
        """

        def set_labels_transform(op: kfp.dsl.ContainerOp) -> kfp.dsl.ContainerOp:
            [  # pylint: disable=expression-not-assigned
                op.add_pod_label(name, value) for name, value in labels.items()
            ]
            return op

        self._transforms.append(set_labels_transform)
        return self

    def add_env_vars(self, env_vars: Dict[str, str]) -> "ContainerOpTransform":
        """Update the transform function to set the provided env vars to the ContainerOp.

        Args:
            env_vars (Dict[str, str]): dict of env vars keys and values.
        """

        def set_env_vars_transform(op: kfp.dsl.ContainerOp) -> kfp.dsl.ContainerOp:
            [  # pylint: disable=expression-not-assigned
                op.add_env_variable(k8s.V1EnvVar(name, value))
                for name, value in env_vars.items()
            ]
            return op

        self._transforms.append(set_env_vars_transform)
        return self

    def add_env_var(self, name: str, value: str) -> "ContainerOpTransform":
        """Update the transform function to set the provided env var to the ContainerOp.

        Args:
            name (str): name of the env var.
            value (str): value of the env var.

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """
        self._transforms.append(
            lambda op: op.container.add_env_variable(k8s.V1EnvVar(name, value))
        )
        return self

    def add_env_var_from_secret(
        self, name: str, secret_name: str, secret_key: str
    ) -> "ContainerOpTransform":
        """Update the transform function to set the provided env var from a k8s secret.

        Args:
            name (str): name of the env var.
            secret_name (str): name of the k8s secret.
            secret_key (str): key to retrieve from the k8s secret.

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """
        self._transforms.append(
            lambda op: op.container.add_env_variable(
                k8s.V1EnvVar(
                    name,
                    value_from=k8s.V1EnvVarSource(
                        secret_key_ref=k8s.V1SecretKeySelector(
                            key=secret_key, name=secret_name
                        )
                    ),
                )
            )
        )
        return self

    def add_env_var_from_configmap(self, configmap_name: str) -> "ContainerOpTransform":
        """Update the transform function to set env vars from a configmap.

        Args:
            configmap_name (str): name of the configmap.

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """
        self._transforms.append(
            lambda op: op.container.add_env_from(
                k8s.V1EnvFromSource(
                    config_map_ref=k8s.V1ConfigMapEnvSource(name=configmap_name)
                )
            )
        )
        return self

    def set_cpu_resources(
        self, request: Union[int, str], limit: Union[int, str] = None
    ) -> "ContainerOpTransform":
        """Update the transform function to set the cpu resources for the main container.

        Args:
            request (Union[int, str]): How much cpu to request.
            limit (Union[int, str], optional): Max cpu load before throttling. Defaults to None.

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """

        self._transforms.append(
            lambda op: op.container.set_cpu_request(str(request)).set_cpu_limit(
                str(limit or request)
            )
        )

        return self

    def set_memory_resources(
        self, request: Union[int, str], limit: Union[int, str] = None
    ) -> "ContainerOpTransform":
        """Update the transform function to set the memory resources for the main container.

        Args:
            request (Union[int, str]): How much memory to request.
            limit (Union[int, str], optional): Max memory before killing the pod. Defaults to None.

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """
        self._transforms.append(
            lambda op: op.container.set_memory_request(str(request)).set_memory_limit(
                str(limit or request)
            )
        )

        return self

    def set_gpu_limit(
        self, value: Union[int, str], vendor: str = "nvidia"
    ) -> "ContainerOpTransform":
        """Update the transform function to set the cpu limit for the main container.

        Args:
            value (Union[int, str]): GPU limit for the main container.
            vendor (str, optional): Either "nvidia" or "amd". Defaults to "nvidia".

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """
        self._transforms.append(
            lambda op: op.container.set_gpu_limit(str(value), vendor)
        )
        return self

    def set_image_pull_policy(self, policy: str) -> "ContainerOpTransform":
        """Update the transform function to set the image pull policy for the main container.

        Args:
            policy (str): One of "Always", "Never", "IfNotPresent".

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """
        self._transforms.append(lambda op: op.container.set_image_pull_policy(policy))
        return self

    def set_sidecar_image_pull_policy(
        self, policy: str, sidecar_name: str = "*"
    ) -> "ContainerOpTransform":
        """Update the transform function to set the image pull policy for the sidecars.

        Args:
            policy (str): One of "Always", "Never", "IfNotPresent".
            sidecar_name (str, optional): Glob pattern for sidecar name. Defaults to "*".

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """

        def set_sidecar_transform(op: kfp.dsl.ContainerOp) -> kfp.dsl.ContainerOp:
            [  # pylint: disable=expression-not-assigned
                sidecar.set_image_pull_policy(policy)
                for sidecar in op.sidecars
                if fnmatch(sidecar.name, sidecar_name)
            ]

        self._transforms.append(set_sidecar_transform)
        return self

    def set_resources(
        self,
        cpu: Union[int, str, Tuple[Union[int, str], Union[int, str]]] = None,
        memory: Union[str, Tuple[str, str]] = None,
    ) -> "ContainerOpTransform":
        """Update the transform function to set the cpu and memory resources for the main container.

        If a int or str is provided, the resource request will equal the limit (i.e. QoS is Guaranteed).
        Otherwise, a tuple should be provided specifying the request and the limit.

        Args:
            cpu (Union[int, str, Tuple[Union[int, str], Union[int, str]]], optional): A str or tuple representing the cpu request and limit.
            memory (Union[str, Tuple[str, str]], optional): A str or tuple representing the memory request and limit.

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """
        if isinstance(cpu, (tuple, list)):
            cpu_request, cpu_limit = cpu
        else:
            cpu_request = cpu  # type: ignore
            cpu_limit = cpu  # type: ignore

        if isinstance(memory, (tuple, list)):
            memory_request, memory_limit = memory
        else:
            memory_request = memory  # type: ignore
            memory_limit = memory  # type: ignore

        def set_resources_transform(op: kfp.dsl.ContainerOp) -> kfp.dsl.ContainerOp:

            if cpu_request:
                op.container.set_cpu_request(str(cpu_request))
            if cpu_limit:
                op.container.set_cpu_limit(str(cpu_limit))
            if memory_request:
                op.container.set_memory_request(memory_request)
            if memory_limit:
                op.container.set_memory_limit(memory_limit)
            return op

        self._transforms.append(set_resources_transform)
        return self

    def set_sidecar_resources(
        self,
        cpu: Union[int, str, Tuple[Union[int, str], Union[int, str]]] = None,
        memory: Union[str, Tuple[str, str]] = None,
        sidecar_name: str = "*",
    ) -> "ContainerOpTransform":
        """Update the transform function to set the cpu and memory resources for the sidecars.

        If a int or str is provided, the resource request will equal the limit (i.e. QoS is Guaranteed).
        Otherwise, a tuple should be provided specifying the request and the limit.

        Args:
            cpu (Union[int, str, Tuple[Union[int, str], Union[int, str]]], optional): A str or tuple representing the cpu request and limit.
            memory (Union[str, Tuple[str, str]], optional): A str or tuple representing the memory request and limit.
            sidecar_name (str, optional): Glob pattern matching the sidecar name. Defaults to "*".

        Returns:
            ContainerOpTransform: updated ContainerOpTransform object.
        """
        if isinstance(cpu, (tuple, list)):
            cpu_request, cpu_limit = cpu
        else:
            cpu_request = cpu  # type: ignore
            cpu_limit = cpu  # type: ignore

        if isinstance(memory, (tuple, list)):
            memory_request, memory_limit = memory
        else:
            memory_request = memory  # type: ignore
            memory_limit = memory  # type: ignore

        def set_sidecar_resources_transform(
            op: kfp.dsl.ContainerOp,
        ) -> kfp.dsl.ContainerOp:
            for sidecar in op.sidecars:
                if fnmatch(sidecar.name, sidecar_name):
                    if cpu_request:
                        sidecar.set_cpu_request(str(cpu_request))
                    if cpu_limit:
                        sidecar.set_cpu_limit(str(cpu_limit))
                    if memory_request:
                        sidecar.set_memory_request(memory_request)
                    if memory_limit:
                        sidecar.set_memory_limit(memory_limit)
            return op

        self._transforms.append(set_sidecar_resources_transform)
        return self
