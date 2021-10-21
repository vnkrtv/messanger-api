FROM snakepacker/python:all as builder
MAINTAINER vnkrtv

COPY requirements.txt /mnt/
RUN python3.8 -m venv /usr/share/python3/venv \
 && /usr/share/python3/venv/bin/pip install -U pip \
 && /usr/share/python3/venv/bin/pip install -Ur /mnt/requirements.txt

FROM snakepacker/python:3.8 as base

COPY --from=builder /usr/share/python3/venv /usr/share/python3/venv
COPY . /usr/share/python3/
COPY deploy/entrypoint /entrypoint

ENTRYPOINT ["/entrypoint"]
