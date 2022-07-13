import os

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from distributed import Client
from flytekit import (
    ExecutionParameters,
    FlyteContextManager,
    PythonFunctionTask,
    Resources,
)
from flytekit.extend import ExecutionState, TaskPlugins

from bstadlbauer.flytekitplugins.dask.errors import UnsupportedResourcesError

def _get_docker_image() -> str:
    docker_image = os.getenv(DOCKER_IMAGE_ENV_VAR, "")
    if docker_image == "":
        raise ValueError(
            f"Could not determine the current docker image to use for the dask cluster."
            f"Please either make sure that the '{DOCKER_IMAGE_ENV_VAR}' is set or to "
            f"provide the `image` argument in the corresponding `Dask()` configuration."
            f""
            f"For a tutorial on how to do so, checkout: "
            f"https://github.com/pachama/pachama-flyte/blob/main/docs/adding_docker_image_env_var.md"
        )
    return docker_image


def _fail_with_unsupported_resources(resources: Resources):
    if (
        resources.gpu is not None
        or resources.ephemeral_storage is not None
        or resources.storage is not None
    ):
        raise UnsupportedResourcesError(
            "At the moment, we only support setting `cpu` and `mem` with `dask` "
            f"resources. Your specified resources are {resources}"
        )


def _convert_flyte_resources_to_dict(
    requests: Optional[Resources], limits: Optional[Resources]
) -> Optional[Dict[str, Dict[str, str]]]:
    resources_dict = {}
    if requests is not None:
        _fail_with_unsupported_resources(requests)
        resources_dict["requests"] = {"cpu": requests.cpu, "memory": requests.mem}
    if limits is not None:
        _fail_with_unsupported_resources(limits)
        resources_dict["limits"] = {"cpu": limits.cpu, "memory": limits.mem}
    if resources_dict == {}:
        return None
    return resources_dict


class DaskFunctionTask(PythonFunctionTask[Dask]):
    """Plugin which deploys a dask cluster before running the code"""

    _DASK_TASK_TYPE = "dask"

    def __init__(self, task_config: Dask, task_function: Callable, **kwargs):
        super(DaskFunctionTask, self).__init__(
            task_config=task_config,
            task_type=self._DASK_TASK_TYPE,
            task_function=task_function,
            **kwargs,
        )
        self._cluster: Optional["KubeCluster"] = None
        self.dask_client: Optional[Client] = None

    def pre_execute(self, user_params: ExecutionParameters) -> ExecutionParameters:
        ctx = FlyteContextManager.current_context()
        is_local_run = not (
            ctx.execution_state
            and ctx.execution_state.mode == ExecutionState.Mode.TASK_EXECUTION
        )
        if is_local_run:
            cluster = None
            client = Client()
        else:
            # Local import because otherwise this checks directly for a valid
            # kubectl configuration
            from dask_kubernetes.experimental import KubeCluster

            cluster = KubeCluster(
                name=f"flyte-{user_params.execution_id.name}",
                namespace=self.task_config.namespace,
                image=self.task_config.image or _get_docker_image(),
                n_workers=self.task_config.n_workers,
                resources=_convert_flyte_resources_to_dict(
                    self.task_config.requests, self.task_config.limits
                ),
                env=self.task_config.env,
            )
            # FIXME: Temporarily removed, does not seem to work
            # Issue is tracked here: https://github.com/pachama/pachama-flyte/issues/2
            # for worker_group in self.task_config.additional_worker_groups:
            #     cluster.add_worker_group(
            #         name=worker_group.name,
            #         n_workers=worker_group.n_workers,
            #         image=worker_group.image or _get_docker_image(),
            #         resources=_convert_flyte_resources_to_dict(
            #             worker_group.requests, worker_group.limits
            #         ),
            #         env=worker_group.env,
            #     )
            self._cluster = cluster
            client = Client(cluster)
        self.dask_client = client
        return (
            user_params.builder()
            .add_attr("DASK_CLIENT", client)
            .add_attr("DASK_CLUSTER", cluster)
            .build()
        )

    def post_execute(self, user_params: ExecutionParameters, rval: Any) -> Any:
        if self.dask_client is not None:
            self.dask_client.close()
        if self._cluster is not None:
            self._cluster.close()
        return rval


TaskPlugins.register_pythontask_plugin(Dask, DaskFunctionTask)
