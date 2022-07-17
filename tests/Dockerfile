# syntax=docker/dockerfile:1.4
FROM python:3.8-slim

RUN apt-get update  \
    && apt-get install -y \
      curl \
      git \
      groff \
      unzip \
    && rm -rf /var/lib/apt/lists/*


# Install awscli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip "awscliv2.zip" \
    && ./aws/install \
    && rm "awscliv2.zip"

# Need to add --endpoint_url to `aws`, thus wrapping the original
ENV AWS_ACCESS_KEY_ID=minio
ENV AWS_SECRET_ACCESS_KEY=miniostorage
RUN mkdir -p /root/.local/bin \
    && echo '#!/bin/bash\n/usr/local/bin/aws --endpoint-url http://minio.flyte.svc.cluster.local:9000 "$@"' > /root/.local/bin/aws \
    && chmod +x /root/.local/bin/aws
# Also used for poetry
ENV PATH "/root/.local/bin:$PATH"

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry config cache-dir /root/.cache \
    && poetry config virtualenvs.create false


WORKDIR /src

# Install dependencies. Package is not required as it will be serialized in
COPY pyproject.toml .
COPY poetry.lock .
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root

COPY ./tests/ ./tests
COPY ./bstadlbauer/ ./bstadlbauer
RUN poetry install
ENV PYTHONPATH "/root:$PYTHONPATH"

ARG DOCKER_IMAGE
ENV FLYTEKITPLUGIN_DASK_DOCKER_IMAGE $DOCKER_IMAGE

ENTRYPOINT []
