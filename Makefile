export DOCKER_BUILDKIT=1
DOCKER_IMAGE = "flytekitplugins-dask:dev"

.PHONY: build
docker-build:
	docker build -t ${DOCKER_IMAGE} . -f tests/Dockerfile --build-arg DOCKER_IMAGE=${DOCKER_IMAGE}

.PHONY: run
docker-run: docker-build
	docker run -it --rm ${DOCKER_IMAGE}

.PHONY: setup
setup:
	poetry install
	poetry run pre-commit install

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: test
test:
	poetry run pytest

.PHONY: shutdown-cluster
shutdown-cluster:
	cd tests/.pytest-kind/pytest-kind \
	&& ./kind-* delete cluster --name pytest-kind
