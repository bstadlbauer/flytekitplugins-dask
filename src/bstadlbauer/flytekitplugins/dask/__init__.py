from flytekit.core.task import TaskPlugins

from bstadlbauer.flytekitplugins.dask.config import Dask
from bstadlbauer.flytekitplugins.dask.task import DaskFunctionTask

TaskPlugins.register_pythontask_plugin(Dask, DaskFunctionTask)
