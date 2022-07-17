import os
from typing import Optional

import flytekit
from dask_kubernetes.experimental import KubeCluster
from distributed import Client
from flytekit import Resources, task, workflow

from bstadlbauer.flytekitplugins.dask import Dask


@task(task_config=Dask())
def dask_test_task():
    ctx = flytekit.current_context()
    client = ctx.dask_client  # type: Client
    cluster = ctx.dask_cluster  # Optional[KubeCluster]
    assert client is not None
    assert cluster is not None

    def add_one(x: int) -> int:
        return x + 1

    future = client.submit(add_one, 1)
    result = future.result()  # blocks until future is ready
    assert result == 2


@task(
    task_config=Dask(
        n_workers=1,
        requests=Resources(cpu="100m", mem="200Mi"),
        limits=Resources(cpu="100m", mem="200Mi"),
        env={"foo": "bar"},
        namespace="dask-test-development",
    )
)
def dask_test_task_with_configuration():
    ctx = flytekit.current_context()
    client = ctx.dask_client  # type: Client
    cluster = ctx.dask_cluster  # type: Optional[KubeCluster]
    print(client, flush=True)
    print(cluster, flush=True)
    assert cluster.n_workers == 1
    assert cluster.namespace == "dask-test-development"

    def get_env() -> None:
        assert os.environ["foo"] == "bar"

    future = client.submit(get_env)
    future.result()  # blocks until future is ready


@workflow
def demo_workflow():
    dask_test_task()
    dask_test_task_with_configuration()
