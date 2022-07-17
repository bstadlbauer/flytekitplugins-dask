import dask.array as da
import flytekit
from flytekit import task, workflow

from bstadlbauer.flytekitplugins.dask import Dask


@task(task_config=Dask())
def my_task() -> float:
    current_context = flytekit.current_context()
    client = current_context.dask_client
    cluster = current_context.dask_cluster
    assert cluster is None
    assert client is not None
    array = da.from_array([1] * 1000, chunks=(100))
    return float(array.mean().compute())


@workflow
def my_workflow() -> float:
    return my_task()


def test_local_dask_task():
    assert my_workflow() == 1.0
