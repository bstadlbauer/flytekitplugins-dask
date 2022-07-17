import logging
import os
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from _pytest.tmpdir import TempPathFactory
from dask_kubernetes.common.utils import check_dependency
from flytekit.configuration import Config, PlatformConfig
from flytekit.remote import FlyteRemote
from pytest_kind import KindCluster

check_dependency("docker")
check_dependency("helm")
check_dependency("kubectl")
check_dependency("flytectl")

# TODO: add constant for flyte and dask version
_logger = logging.getLogger(__name__)

_ENV_FILE = Path(__file__).parent.parent / ".env"


_FLYTE_INGRESS_PORT = 30081
_FLYTE_ADMIN_ENDPOINT = f"localhost:{_FLYTE_INGRESS_PORT}"
_MINIO_PORT = 30084
_FLYTE_PROJECT_ID = "dask-test"
_FLYTE_DOMAIN = "development"
_TESTS_DIR_PATH = Path(__file__).parent
_FLYTE_DASK_OPERATOR_ROLE_BINDING_MANIFEST = (
    _TESTS_DIR_PATH / "k8s" / "flyte-dask-cluster-role-binding.yaml"
)


@pytest.fixture(scope="session")
def _k8s_cluster(kind_cluster: KindCluster) -> Generator[KindCluster, None, None]:
    os.environ["KUBECONFIG"] = str(kind_cluster.kubeconfig_path)
    kind_cluster.ensure_kubectl()
    yield kind_cluster
    del os.environ["KUBECONFIG"]


@pytest.fixture(scope="session")
def _docker_image(_k8s_cluster: KindCluster) -> str:
    _logger.info("Starting to build test docker image")
    image_name = f"flytekitplugins-dask:dev-{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
    os.environ["DOCKER_BUILDKIT"] = "1"
    subprocess.check_output(
        [
            "docker",
            "build",
            "-t",
            image_name,
            ".",
            "-f",
            "tests/Dockerfile",
            "--build-arg",
            f"DOCKER_IMAGE={image_name}",
        ],
        cwd=str(_TESTS_DIR_PATH.parent),
    )
    _logger.info("Finished to build test docker image")
    _k8s_cluster.load_docker_image(image_name)
    return image_name


@pytest.fixture(scope="session")
def _dask_operator_installation(_k8s_cluster: KindCluster) -> None:
    _logger.info("Installing the dask operator into the kind cluster")
    subprocess.check_output(["helm", "repo", "add", "dask", "https://helm.dask.org"])
    subprocess.check_output(
        [
            "helm",
            "upgrade",
            "--install",
            "-n",
            "dask",
            "dask",
            "dask/dask-kubernetes-operator",
            "--create-namespace",
            "--wait",
            "--set",
            "image.tag=2022.5.2",
        ],
    )
    _logger.info("Finished installing dask operator into the kind cluster")


@pytest.fixture(scope="session")
def _flyte_installation(
    _k8s_cluster: KindCluster,
    _dask_operator_installation: None,
) -> Generator[None, None, None]:
    _logger.info("Installing flyte into the kind cluster")
    flyte_namespace = "flyte"
    subprocess.check_output(
        ["helm", "repo", "add", "flyteorg", "https://helm.flyte.org"]
    )
    subprocess.check_output(
        [
            "helm",
            "upgrade",
            "--install",
            "-n",
            flyte_namespace,
            "flyte",
            "flyteorg/flyte",
            "--create-namespace",
            "--wait",
        ],
    )
    _k8s_cluster.kubectl("apply", "-f", str(_FLYTE_DASK_OPERATOR_ROLE_BINDING_MANIFEST))
    with _k8s_cluster.port_forward(
        "service/flyte-contour-envoy",
        80,
        "-n",
        flyte_namespace,
        local_port=_FLYTE_INGRESS_PORT,
    ), _k8s_cluster.port_forward(
        "service/minio",
        9000,
        "-n",
        flyte_namespace,
        local_port=_MINIO_PORT,
    ):
        _logger.info("Finished installing flyte into the kind cluster")
        yield


@pytest.fixture(scope="session")
def _flyte_project(_flyte_installation: None) -> None:
    output = subprocess.run(
        [
            "flytectl",
            "--admin.endpoint",
            _FLYTE_ADMIN_ENDPOINT,
            "--admin.insecure",
            "true",
            "create",
            "project",
            "--id",
            _FLYTE_PROJECT_ID,
            "--name",
            "flyteplugins-dask",
            "--description",
            "Test project for flyteplugins-dask",
        ],
        stderr=subprocess.PIPE,
    )
    if output.returncode != 0:
        # It's ok if the project already exists
        if b"value with matching already exists" in output.stderr:
            return
        output.check_returncode()
    print()


@pytest.fixture(scope="session")
def flyte_registration_version() -> str:
    return (
        f"flyte-pytest-{datetime.now().strftime('%Y-%m-%d_%H:%M')}"
        f"-{str(uuid.uuid4())[:8]}"
    )


@pytest.fixture(scope="session")
def _registered_flyte_workflows(
    flyte_registration_version: str,
    _flyte_project: None,
    _docker_image: str,
    tmp_path_factory: TempPathFactory,
) -> None:
    workflow_dir = tmp_path_factory.mktemp("workflows")
    subprocess.check_output(
        [
            "pyflyte",
            "-k",
            "tests",
            "serialize",
            "--image",
            _docker_image,
            "workflows",
            "-f",
            str(workflow_dir),
        ],
        cwd=str(_TESTS_DIR_PATH.parent),
    )
    subprocess.check_output(
        [
            "flytectl",
            "--admin.endpoint",
            _FLYTE_ADMIN_ENDPOINT,
            "--admin.insecure",
            "true",
            "register",
            "files",
            str(workflow_dir / "*"),
            "-p",
            _FLYTE_PROJECT_ID,
            "-d",
            _FLYTE_DOMAIN,
            "--version",
            flyte_registration_version,
        ]
    )


@pytest.fixture(scope="session")
def flyte_remote(_registered_flyte_workflows: None) -> FlyteRemote:
    return FlyteRemote(
        config=Config(
            platform=PlatformConfig(endpoint=_FLYTE_ADMIN_ENDPOINT, insecure=True)
        ),
        default_project=_FLYTE_PROJECT_ID,
        default_domain=_FLYTE_DOMAIN,
    )
