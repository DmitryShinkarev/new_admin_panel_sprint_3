import sqlite3
import logging
import sys
from dataclasses import astuple

logger = logging.getLogger()

class SQLiteLoader():
    def __init__(self, connection: sqlite3.Connection,
                 sort_column: str, name_table: str, model):
        self.conn = connection
        self.conn.row_factory = self.dict_factory
        self.sort_column = sort_column
        self.model = model
        self.name_table = name_table

    @staticmethod
    def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def load_movies(self):

        sort_column = self.sort_column
        name_table = self.name_table

        consq = self.conn
        cursq = consq.cursor()

        batchsize = 500

        sqlite_select_query = f"""SELECT {sort_column} FROM {name_table}"""
        cursq.execute(sqlite_select_query)

        while True:

            records = cursq.fetchmany(batchsize)
            data_values = []

            if not records:
                break

            try:

                for row in records:

                    data = self.model(**row)
                    data_values.append(astuple(data))

                yield data_values

            except sqlite3.DatabaseError as e:
                logger.info('Error %s' % e)
                sys.exit(1)