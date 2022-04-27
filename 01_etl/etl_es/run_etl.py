import logging
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
from redis import Redis
from elasticsearch import Elasticsearch

from utils.backoff import backoff
from utils.etlredis import RedisStorage
from utils.postgres_to_es import ETL

logger = logging.getLogger()

load_dotenv()


@backoff(logger=logger)
def connect_pstgres():

    dsl = {
        'dbname': os.environ.get('POSTGRES_DB'),
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'host': os.environ.get('POSTGRES_HOST'),
        'port': os.environ.get('POSTGRRES_PORT'),
        'options': os.environ.get('POSTGRES_SHEMA')
    }

    return psycopg2.connect(**dsl, cursor_factory=DictCursor)


@backoff(logger=logger)
def connect_redis_strg():
    host_redis = os.environ.get('REDIS_HOST')
    redis_adapter = Redis(host=host_redis,
                          charset="utf-8",
                          decode_responses=True)
    return RedisStorage(redis_adapter=redis_adapter)

@backoff(logger=logger)
def es_conn():
    return Elasticsearch(hosts=os.environ.get("ELASTIC_HOST"))


if __name__ == '__main__':

    with connect_pstgres() as pg_conn:
        redis_strg = connect_redis_strg()
        etl = ETL(conn=pg_conn, redis=redis_strg, es_conn=es_conn())
        etl.stop()
        etl.start()

    pg_conn.close()
    logger.info("** End **")
