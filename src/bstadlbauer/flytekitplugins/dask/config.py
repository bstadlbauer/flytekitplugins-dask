from dataclasses import dataclass
from typing import Dict, Optional

from flytekit import Resources

# FIXME: Re-add this as soon as there is worker group configuration
#        support in dask-kubernetes, at the moment, it seems like the
#        configuration here would have no effect
#        https://github.com/dask/dask-kubernetes/blob/e83e22f032f0f0e990a04589ae5246e7eee63560/dask_kubernetes/experimental/kubecluster.py#L352-L375
# @dataclass
# class WorkerGroup:
#     """Configuration for a dask worker group
#
#     Attributes
#         name:
#             Name of the worker group.
#         n_workers:
#             Number of workers to initially setup. Optional, default to 3
#         image:
#             Image to use for the worker group. Optional, if None (default), uses the
#             same image as the Flyte task
#         requests:
#             Resource requests to be passed to the underlying pods. Optional; If None,
#             will use the cluster default. At the moment, only `cpu` and `mem` will be
#             honored.
#         limits:
#             Resource requests to be passed to the underlying pods. Optional; If None,
#             will use the cluster default. At the moment, only `cpu` and `mem` will be
#             honored.
#         env:
#             List of environment variables to pass to worker pod. Optional; If None
#             will, use the cluster default.
#
#     """
#
#     name: str
#     n_workers: int = 3
#     image: Optional[str] = None
#     requests: Optional[Resources] = None
#     limits: Optional[Resources] = None
#     env: Optional[Dict[str, str]] = None


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

    """

    n_workers: int = 3
    image: Optional[str] = None
    requests: Optional[Resources] = None
    limits: Optional[Resources] = None
    env: Optional[Dict[str, str]] = None
    namespace: str = "dask"

    # FIXME: Check the above comment on re-adding this as soon as it is supported in
    #        `dask-kubernetes`
    # additional_worker_groups: List[WorkerGroup] = field(default_factory=list)
