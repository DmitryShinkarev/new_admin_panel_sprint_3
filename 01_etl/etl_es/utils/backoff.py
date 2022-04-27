from functools import wraps
from time import sleep

import psycopg2
import logging

from elasticsearch.exceptions import ElasticsearchException
from redis.exceptions import RedisError

logger = logging.getLogger()

def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=30, logger=logger):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания
    (border_sleep_time)
    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):
            t = start_sleep_time
            errors_count = 0
            max_errors_count = 10

            while True:
                try:
                    return func(*args, **kwargs)

                except ElasticsearchException as error:
                    msg = f"Error connect to Elasticsearch: {error}"
                except RedisError as error:
                    msg = f"Error connect to Redis: {error}"
                except psycopg2.Error as error:
                    msg = f"Error connect to Postgres: {error}"
                except Exception as error:
                    msg = f"Unknown error: {error}"

                logger.error(msg)

                if t < border_sleep_time:
                    t = t * factor
                else:
                    t = border_sleep_time

                logger.info(f"{msg}, sleep {t} sec.")
                errors_count += 1

                sleep(t)

                if errors_count > max_errors_count:
                    name_func = func.__name__
                    msg = f"Max errors count of {name_func}"
                    logger.critical(msg)
                    break

        return inner

    return func_wrapper
