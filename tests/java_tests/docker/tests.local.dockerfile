FROM docker:20.10

RUN   apk --no-cache add openjdk11 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community
RUN   apk add curl wget git tar unzip ca-certificates gradle=6.8.3-r1

WORKDIR /opt/messenger/tests/

COPY  build.gradle ./
COPY  src ./src

# you are expected to pass envvar IMAGE_NAME
CMD   gradle test -i