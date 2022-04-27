
FROM python:3.9.6-slim-bullseye

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN set -xe; \
    apt-get update -yqq && \
    apt-get upgrade -yqq && \
    apt-get install -yqq netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# copy entrypoint.sh
COPY ./movies_admin/entrypoint.sh /usr/src/app/entrypoint.sh

COPY movies_admin/requirements.txt /usr/src/app

# install dependencies
RUN pip install --upgrade pip && \ 
    pip install -r requirements.txt --no-cache-dir

# copy project
COPY ./movies_admin /usr/src/app/

# run entrypoint.sh
ENTRYPOINT ["bash", "/usr/src/app/entrypoint.sh"]
