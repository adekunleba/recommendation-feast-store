FROM python:3.8-slim-buster AS app
LABEL maintainer="Adekunle Babatunde <adekunleba@gmail.com>"

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
  && apt install bzip2 curl git wget ca-certificates subversion procps openssh-client mercurial libxrender1 libxext6 libsm6 libglib2.0-0 cmake ack g++ python3-dev python3-pip -yq \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  # && addgroup python \ 
  && adduser --system --group python \
  && chown python:python -R /app \
  && apt-get install g++-8 -yq \
  && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 800 --slave /usr/bin/g++ g++ /usr/bin/g++-8 \
  && pip3 install --upgrade --force pip \
  && chown python:python -R /usr
USER python

COPY --chown=python:python requirements*.txt ./

RUN pip install --user -r ./requirements.txt 

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
RUN cd /app/feast && make install-python-ci-dependencies
RUN cd /app/feast/sdk/python && pip install -e .

# End install feast
RUN cd /app

# Copy project files
COPY --chown=python:python bin/ ./bin

# Ad click datasets
COPY --chown=python:python ContextAdClickData.py ./ContextAdClickData.py
COPY --chown=python:python FeastUtility.py ./FeastUtility.py

RUN chmod 0755 bin/*
RUN chmod +x bin/docker-entrypoint.sh

RUN ls -lh
# Just a comment
# We can move this to a bash shell to run the commands
CMD [ "python", "FeastUtility.py" ]