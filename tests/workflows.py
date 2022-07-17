import time

import flytekit
from dask_kubernetes.experimental import KubeCluster
from distributed import Client
from flytekit import task, workflow

from bstadlbauer.flytekitplugins.dask import Dask
from bstadlbauer.flytekitplugins.dask.config import WorkerGroup


@task(task_config=Dask(additional_worker_groups=[WorkerGroup("second_group")]))
def demo_task():
    ctx = flytekit.current_context()
    client = ctx.dask_client  # type: Client
    cluster = ctx.dask_cluster  # type: KubeCluster
    print(client, flush=True)
    print(cluster, flush=True)
    time.sleep(1000)


@workflow
def demo_workflow():
    return demo_task()
