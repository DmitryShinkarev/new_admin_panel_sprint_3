import logging
import os
import sqlite3

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from datamodels import Genre, Genre_film_work, Movie, Person, Person_film_work
from postgres_saver import PostgresSaver
from sqlite_loader import SQLiteLoader

logger = logging.getLogger()

load_dotenv()

LIST_MODEL_TABLES = [{
    'table_name':'film_work',
    'model': Movie,
    'sort_columns_sqlt':"""id, title, description, rating,
                            creation_date, type, created_at as created,
                            updated_at as modified"""
}, {
    'table_name':'genre',
    'model':Genre,
    'sort_columns_sqlt':"""id, name, description,
                        datetime('now') as created,
                        datetime('now') as modified"""
}, {
    'table_name':'person',
    'model':Person,
    'sort_columns_sqlt':"""id, full_name, birth_date,
                            datetime('now') as created,
                            datetime('now') as modified"""
}, {
    'table_name':'genre_film_work',
    'model':Genre_film_work,
    'sort_columns_sqlt':"""id, genre_id, film_work_id as filmwork_id,
                            datetime('now') as created"""
}, {
    'table_name':'person_film_work',
    'model':Person_film_work,
    'sort_columns_sqlt':"""id, role, person_id,
                            film_work_id as filmwork_id,
                            datetime('now') as created"""
}]


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    for table_model in LIST_MODEL_TABLES:

        model = table_model['model']
        table_name = table_model['table_name']
        sort_column = table_model['sort_columns_sqlt']

        try:
            postgres_saver = PostgresSaver(pg_conn, table_name, model)
            sqlite_loader = SQLiteLoader(connection, sort_column,
                                        table_name, model)

            data = sqlite_loader.load_movies()
            postgres_saver.save_all_data(data)
        except sqlite3.OperationalError:
            logging.exception('Ошибка при выгрузке данных из sqlite')
        except psycopg2.Error:
            logging.exception('Ошибка при загрузке данных в psql')
        except Exception:
            logging.exception('Непредвиденная ошибка')


if __name__ == '__main__':

    dsl = {
        'dbname': os.environ.get('POSTGRES_DB'),
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'host': os.environ.get('POSTGRES_HOST'),
        'port': os.environ.get('POSTGRES_PORT'),
        'options': os.environ.get('POSTGRES_SHEMA')
    }

    path_dbsqlite = './db/db.sqlite'

    logger.info("** Start dataloder sqlite to postgres **")

    with sqlite3.connect(path_dbsqlite) as sqlite_conn, psycopg2.connect(
            **dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)

    sqlite_conn.close()
    pg_conn.close()

    logger.info("** End dataloder sqlite to postgres **")
