FROM python:3.9-slim

WORKDIR /etl

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN set -xe; \
    apt-get update -yqq && \
    apt-get upgrade -yqq && \
    apt-get install -yqq netcat

# Clean up
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY entrypoint.sh /etl/
COPY requirements.txt /etl/

# install dependencies
RUN pip install --upgrade pip && \ 
    pip install -r requirements.txt --no-cache-dir

ENTRYPOINT ["bash", "/etl/entrypoint.sh"]