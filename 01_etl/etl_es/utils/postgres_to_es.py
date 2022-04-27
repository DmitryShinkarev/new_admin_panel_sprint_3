import json
import logging
import os
from datetime import datetime
from time import sleep
from typing import Generator

from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection
from psycopg2.extras import RealDictCursor

from utils.backoff import backoff
from utils.encoder import EnhancedJSONEncoder, coroutine
from utils.esindex import MOVIES_INDEX
from utils.etlmodels import ETLMovie
from utils.etlredis import RedisStorage
from utils.sql_queries import GENRES_QUERY, MOVIES_QUERY, PERSONS_QUERY

logger = logging.getLogger()

from dotenv import load_dotenv

load_dotenv()


class ETL:
    def __init__(
        self,
        conn: _connection,
        redis: RedisStorage,
        es_conn: Elasticsearch,
    ):
        self.conn = conn
        self.es = es_conn
        self.redis = redis
        self.batch_size = 10

    @backoff(logger=logger)
    def worker(self, thread):
        logger.info("** Start **")
        while self.redis.get_status("etl") == "running":
            thread.send(1)
            sleep(0.01)

    @coroutine
    def extract(self, enricher: Generator) -> Generator:
        """
        Тут работает немного не так как было описано.
        Сначала проходят два запроса из таблиц Жанры и Персоны
        на изменившиеся строки по дате модификации и в enricher
        забирается уникальный массив id связанных фильмов в хранилище
        Redis. После этого итоги этих запросов вылетают из цикла
        не загрузившись в es.
        Последней идет запрос с фильмами. Где одним запросом через 
        union берутся строки изменившихся фильмов по дате модификации
        а так же все фильмы с поиском по идентификатору, 
        который мы сохранили ранее в редис и уже далее эти данные
        в соответствии с схемой через датакласс приходят в es.
        """
        logger.info("** Extract DB Postgess **")

        pg_queres = [
            {
                "index": "genres",
                "query": GENRES_QUERY
            },
            {
                "index": "persons",
                "query": PERSONS_QUERY
            },
            {
                "index": "movies",
                "query": MOVIES_QUERY
            },
        ]

        while True:
            _ = (yield)

            for produscer in pg_queres:

                query = produscer["query"]
                index = produscer["index"]

                lasttime = self.redis.get_modified_time(index) or str(
                    datetime(1990, 1, 1))
                movies_id = self.redis.get_modified_filmid()
                movies_id.append("00000000-0000-0000-0000-000000000000")

                with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if index != "movies":
                        cursor.execute(query, (lasttime, ))
                    else:
                        cursor.execute(query, {
                            "lasttime": lasttime,
                            "movies_id": tuple(movies_id)
                        })

                    while True:
                        all_rows = [
                            dict(row)
                            for row in cursor.fetchmany(self.batch_size)
                        ]

                        if not all_rows:
                            break

                        self.redis.set_modified_time(index,
                                                     all_rows[0]["modified"])
                        enricher.send({"index": index, "data": all_rows})

    @coroutine
    def enricher(self, transform: Generator) -> Generator:
        logger.info("** Enricher data **")

        while True:
            result = (yield)

            index = result["index"]
            data_mod_id = result["data"]

            if index != "movies":
                for row in data_mod_id:
                    [
                        self.redis.push_modified_filmid(id["fwid"])
                        for id in row["array_id"]
                    ]
                self.redis.set_modified_time(index, data_mod_id[0]["modified"])

            transform.send(result)

    @coroutine
    def transform(self, load: Generator) -> Generator:
        logger.info("** Transformed data **")

        while True:
            result = (yield)

            index = result["index"]
            data_rows = result["data"]
            transformed_list = []

            for row in data_rows:
                if index == "movies":
                    dataclass = ETLMovie.from_dict_cls({**row})
                    transformed_list.append(dataclass)
                else:
                    continue

            load.send({
                "index": index,
                "data": transformed_list,
                "lasttime": data_rows[0]["modified"]
            })

    @backoff()
    @coroutine
    def load(self) -> Generator:
        logger.info("** Load data **")

        while True:
            transformed = (yield)

            index = transformed["index"]
            data = transformed["data"]
            lasttime = transformed["lasttime"]

            if len(data) == 0:
                continue

            data_to_es = []
            for row in data:
                data_to_es.extend([
                    json.dumps({"index": {
                        "_index": index,
                        "_id": row.id
                    }}),
                    json.dumps(row, cls=EnhancedJSONEncoder),
                ])

            index_data = "\n".join(data_to_es) + "\n"
            self.es.bulk(body=index_data, index=index)
            [self.redis.del_modified_filmid(movie.id) for movie in data]
            self.redis.set_modified_time(index, lasttime)

    def start(self):
        if self.redis.get_status("etl") == "running":
            logger.warning("ETL service already started!")
            return
        else:
            self.redis.set_status("etl", "running")
            #self.es.indices.delete(index="movies", ignore=[400, 404])
            self.es.indices.create(index="movies",
                                   body=MOVIES_INDEX,
                                   ignore=[400, 404])

        load = self.load()
        transform = self.transform(load)
        enricher = self.enricher(transform)
        extract = self.extract(enricher)

        self.worker(extract)

    def stop(self):
        self.redis.set_status("etl", "stop")
        logger.info("etl stopped")
