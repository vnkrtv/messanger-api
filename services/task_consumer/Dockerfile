FROM snakepacker/python:all as builder
MAINTAINER vnkrtv

RUN python3.8 -m venv /usr/share/python3/app \
 && /usr/share/python3/app/bin/pip install -U pip

COPY . /mnt/
WORKDIR /mnt/

RUN /usr/share/python3/app/bin/pip install -U -r requirements.txt \
 && /usr/share/python3/app/bin/pip install .

FROM snakepacker/python:3.8 as base

COPY --from=builder /usr/share/python3/app /usr/share/python3/app
RUN ln -snf /usr/share/python3/app/bin/run-consumer /usr/local/bin/

ENTRYPOINT ["run-consumer"]
