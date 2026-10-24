import json
import logging

import sentry_sdk


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "level": record.levelname,
                "logger_type": record.name,
                "func": record.funcName,
                "msg": record.getMessage(),
            },
            ensure_ascii=False,
        )


def setup(dsn):
    sentry_sdk.init(dsn=dsn, environment="production")
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.getLogger().addHandler(handler)
