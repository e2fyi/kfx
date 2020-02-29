FROM python:3.6-slim as build

WORKDIR /workspace

COPY *.* ./
COPY kfx/ kfx/

RUN python setup.py sdist && ls dist

##################################
FROM python:3.6-slim as dist

WORKDIR /tmp
COPY --from=build /workspace/dist/kfx-*.tar.gz kfx.tar.gz
RUN pip install kfx.tar.gz

WORKDIR /workspace

