import pytest
from flytekit.remote import FlyteRemote, FlyteWorkflow

from tests.workflows import demo_workflow


@pytest.fixture
def _dask_workflow(
    flyte_remote: FlyteRemote, flyte_registration_version: str
) -> FlyteWorkflow:
    workflow_name = f"{demo_workflow.__module__}.{demo_workflow.__name__}"
    return flyte_remote.fetch_workflow(
        name=workflow_name, version=flyte_registration_version
    )


def test_dask_workflow(flyte_remote: FlyteRemote, _dask_workflow: FlyteWorkflow):
    flyte_remote.execute_remote_wf(_dask_workflow, inputs={}, wait=True)
    # FIXME: Check for successful run
