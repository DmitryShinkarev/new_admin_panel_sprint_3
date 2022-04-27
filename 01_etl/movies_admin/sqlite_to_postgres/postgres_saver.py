import sys
import logging
from logging import LoggerAdapter

import psycopg2
from psycopg2.extensions import connection as _connection

logger = logging.getLogger()

class PostgresSaver():
    def __init__(self, connection: _connection, table_name: str, model):
        self.conn = connection
        self.logger = logger
        self.model = model
        self.table_name= table_name
        

    def save_all_data(self, data_list):
        
        name_table = self.table_name

        conpg = self.conn
        curpg = conpg.cursor()
        
        mask = str(self.model.__slots__)
        mask = mask.replace("'",'')
        load_mask = ('%s, '*(len(self.model.__slots__)))[:-2]
        
        curpg.execute(f"""TRUNCATE content.{name_table} CASCADE;""")

        logger = self.logger

        for block in data_list:

            try:

                curpg.executemany("""INSERT INTO %s %s VALUES (%s);""" %
                                  (name_table, mask, load_mask), block)
                conpg.commit()

            except psycopg2.DatabaseError as e:
                logger.info('Error %s' % e)
                sys.exit(1)

        logger.info(f'Created {name_table}')
