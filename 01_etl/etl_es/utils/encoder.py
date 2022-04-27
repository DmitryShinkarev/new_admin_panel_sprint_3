import dataclasses
import datetime
import json
from functools import wraps


def coroutine(coro):

    @wraps(coro)
    def coroinit(*args, **kwargs):
        fn = coro(*args, **kwargs)
        next(fn)
        return fn

    return coroinit


class EnhancedJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)