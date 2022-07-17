# `flytekitplugins-dask`
This plugin is a pure `flytekit` plugin which enables `dask` task support. This is intended
to be a stepping stone, until the work for the (more elaborate) backend (i.e. Flytepropeller)
plugin is finished. The progress of the backend plugin is tracked in
[this GitHub issue](https://github.com/flyteorg/flyte/issues/427).

## Usage
### Installation
To install the plugin, run
```shell
pip install bstadlbauer.flytekitplugins-dask
```
The plugin was prefixed with `bstadlbauer` to avoid a naming conflict with the future "official"
`flytekitplugins-dask`, which will be the `flytekit` counterpart to the backend plugin

### Task definition
To create a `dask` `flyte` task, the only thing you have to do now is to specify the `task_type` to be of kind `Dask`.
Flyte will then handle the lifecycle of the ephemeral `dask` cluster for you.
```python
import flytekit
from flytekit import task, Resources
from bstadlbauer.flytekitplugins.dask import Dask


@task(
    task_config=Dask(
        n_workers=1,
        requests=Resources(cpu="100m", mem="200Mi"),
        limits=Resources(cpu="100m", mem="200Mi"),
        env={"foo": "bar"},
        namespace="my-namespace",
    )
)
def dask_test_task_with_configuration():
    ctx = flytekit.current_context()
    # The client will be a regular distributed.Client() in the local case. Thus, you can also configure it
    # to point to an existing cluster, e.g. by setting the `DASK_SCHEDULER_ADDRESS` environment variable
    client = ctx.dask_client  # type: Client

    # `cluster` will be `None` in the local case
    cluster = ctx.dask_cluster  # type: Optional[KubeCluster]
```

### K8s requirements
This plugin is built on top of the [dask k8s operator](https://kubernetes.dask.org/en/latest/operator.html),
and thus requires the operator to be up and running within your cluster.

Please also make sure that the pods that you are running have permissions to create `DaskCluster` custom resources
for the `kubernetes.dask.org` API.

### Docker image requirements
As it is beneficial to use the same docker image (i.e. same Python environment) for all code related to `dask`,
the plugin expects an environment variable `FLYTEKITPLUGIN_DASK_DOCKER_IMAGE` to be set within the docker image
which runs the Flyte task. It will then use the image from this environment variable to spin up the _scheduler_ as
well as the _worker_ pods of the ephemeral `dask` cluster.


# Contributing
## Development setup
To setup the development environment please run
```shell
make setup
```
this will setup a `poetry` environment and make sure that `pre-commit` hooks are installed correctly.

## Testing
Run the follwing to run all tests:
```shell
make test
```

> Note: There is currently no support for testing on Apple's M1 (aarch; arm64) due to incompatibilities with the `kind`
> cluster

The end-to-end tests use [`pytest-kind`](https://codeberg.org/hjacobs/pytest-kind/src/branch/main/tests) to spin up a
local k8s cluster into which a full Flyte setup, as well as the `dask` operator are installed using their corresponding
`helm` charts.
As setting up the cluster is quite an expensive operation, thus the `--keep-cluster` setting is set by default in the
`pytest` configuration (in `pyproject.toml`). To delete the cluster, you can run
```shell
make shutdown-cluster
```
