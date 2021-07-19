FROM amd64/python:3.9.4-alpine AS app
LABEL maintainer="Adekunle Babatunde <adekunleba@gmail.com>"

WORKDIR /app

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apk update \
  &&  apk add python3-dev build-base \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && addgroup -S python && adduser -S python -G python \
  && chown python:python -R /app

USER python

COPY --chown=python:python requirements*.txt ./

RUN pip install -r ./requirements.txt

# Declare Aruguments
ARG VIEW_LOG_DATA
ENV VIEW_LOG_DATA=${VIEW_LOG_DATA}
ARG TRAIN_DATA
ENV TRAIN_DATA=${TRAIN_DATA}


# install feast dev. - We are using a forked project. We should explore the master branch of feast seems to have s3 support now
ARG FEAST_S3_ENDPOINT_URL
ENV FEAST_S3_ENDPOINT_URL=${FEAST_S3_ENDPOINT_URL}

ARG AWS_ACCESS_KEY_ID
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}

ARG AWS_SECRET_ACCESS_KEY
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

RUN git clone -b mlflow-feast https://github.com/qooba/feast.git
RUN cd feast && make install-python-ci-dependencies
RUN cd sdk/python && pip install -e .

# End install feast
RUN cd /app

# Copy project files
COPY --chown=python:python bin/ ./bin
COPY --chown=python:python feature_store.yaml ./feature_store.yaml
COPY --chown=python:python feature_store.yaml ./feature_store.yaml
# Ad click datasets
COPY --chown=python:python ContextAdClickData.py ./ContextAdClickData.py


RUN chmod 0755 bin/*
RUN chmod +x bin/docker-entrypoint.sh

RUN ls -lh
# Just a comment
# We can move this to a bash shell to run the commands
CMD [ "feast", "apply" ]