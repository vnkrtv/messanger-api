FROM snakepacker/python:all as builder
MAINTAINER vnkrtv

RUN python3.8 -m venv /usr/share/python3/venv \
 && /usr/share/python3/venv/bin/pip install -U pip

COPY . /mnt/
RUN /usr/share/python3/venv/bin/pip install /mnt/

FROM snakepacker/python:3.8 as base

COPY --from=builder /usr/share/python3/venv /usr/share/python3/venv
RUN ln -snf /usr/share/python3/venv/bin/messenger* /usr/local/bin/

COPY deploy/entrypoint /entrypoint

ENTRYPOINT ["/entrypoint"]
