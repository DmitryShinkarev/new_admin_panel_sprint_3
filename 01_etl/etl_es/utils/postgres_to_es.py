import json
import logging
import os
from datetime import datetime, MINYEAR
from time import sleep
from typing import Generator

from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection
from psycopg2.extras import RealDictCursor

from utils.backoff import backoff
from utils.encoder import EnhancedJSONEncoder, coroutine
from utils.esindex import MOVIES_INDEX, GENRES_INDEX, PERSONS_INDEX
from utils.etlmodels import ETLMovie, ETLGenre, ETLPerson
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

        while _ := (yield):

            for producer in pg_queres:

                query = producer["query"]
                index = producer["index"]

                lasttime = self.redis.get_modified_time(index) or str(
                    datetime(MINYEAR, 1, 1, tzinfo=None))
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

        while result := (yield):

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

        while result := (yield):

            index = result["index"]
            data_rows = result["data"]
            transformed_list = []

            for row in data_rows:
                if index == "movies":
                    dataclass = ETLMovie.from_dict_cls({**row})
                elif index == "genres":
                    dataclass = ETLGenre.from_dict_cls({**row})
                elif index == "persons":
                    dataclass = ETLPerson.from_dict_cls({**row})
                else:
                    continue

                transformed_list.append(dataclass)

            load.send({
                "index": index,
                "data": transformed_list,
                "lasttime": data_rows[0]["modified"]
            })

    @backoff()
    @coroutine
    def load(self) -> Generator:
        logger.info("** Load data **")

        while transformed := (yield):

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
            
            self.es.indices.create(index="movies",
                                   body=MOVIES_INDEX,
                                   ignore=[400, 404])

            self.es.indices.create(index="genres",
                                   body=GENRES_INDEX,
                                   ignore=[400, 404])

            self.es.indices.create(index="persons",
                                   body=PERSONS_INDEX,
                                   ignore=[400, 404])

        load = self.load()
        transform = self.transform(load)
        enricher = self.enricher(transform)
        extract = self.extract(enricher)

        self.worker(extract)

    def stop(self):
        self.redis.set_status("etl", "stop")
        logger.info("etl stopped")
