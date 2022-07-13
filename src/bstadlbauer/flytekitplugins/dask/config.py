from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class WorkerGroup:
    """Configuration for a dask worker group

    Attributes
        name:
            Name of the worker group.
        n_workers:
            Number of workers to initially setup. Optional, default to 3
        image:
            Image to use for the worker group. Optional, if None (default), uses the
            same image as the Flyte task
        requests:
            Resource requests to be passed to the underlying pods. Optional; If None,
            will use the cluster default. At the moment, only `cpu` and `mem` will be
            honored.
        limits:
            Resource requests to be passed to the underlying pods. Optional; If None,
            will use the cluster default. At the moment, only `cpu` and `mem` will be
            honored.
        env:
            List of environment variables to pass to worker pod. Optional; If None will,
            use the cluster default.

    """

    name: str
    n_workers: int = 3
    image: Optional[str] = None
    requests: Optional[Resources] = None
    limits: Optional[Resources] = None
    env: Optional[Dict[str, str]] = None


@dataclass
class Dask:
    """Configuration for a `dask` Flyte task

    Attributes:
        n_workers:
            Number of workers to initially setup. Optional, default to 3
        image:
            Image to use for the worker group. Optional, if None (default), uses the
            same image as the Flyte task
        requests:
            Resource requests to be passed to the underlying pods. Optional; If None,
            will use the cluster default. At the moment, only `cpu` and `mem` will be
            honored.
        limits:
            Resource requests to be passed to the underlying pods. Optional; If None,
            will use the cluster default. At the moment, only `cpu` and `mem` will be
            honored.
        env:
            List of environment variables to pass to worker pod. Optional; If None will,
            use the cluster default.
        namespace:
            Kubernetes namespace to deploy the cluster to. Defaults to `dask`
        additional_worker_groups:
            List of additional worker groups to create

    """

    n_workers: int = 3
    image: Optional[str] = None
    requests: Optional[Resources] = None
    limits: Optional[Resources] = None
    env: Optional[Dict[str, str]] = None
    namespace: str = "dask"
    # FIXME: Temporarily removed, does not seem to work
    # Issue is tracked here: https://github.com/pachama/pachama-flyte/issues/2
    # additional_worker_groups: List[WorkerGroupConfig] = field(default_factory=list)
