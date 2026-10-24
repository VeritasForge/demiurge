import json
import logging

import sentry_sdk


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "severity": record.levelname,
                "logger_name": record.name,
                "handler": record.funcName,
                "event": record.getMessage(),
            },
            ensure_ascii=False,
        )


def setup(dsn):
    sentry_sdk.init(dsn=dsn, environment="production")
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.getLogger().addHandler(handler)
