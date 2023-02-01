import logging.config
import os

LOGS_FOLDER_PATH = "logs"


def load_logger_config(log_file_path="logs", level="DEBUG"):
    log_config = {
        "version": 1,
        "formatters": {
            "extend": {
                "format": "[%(asctime)s] [%(process)d] [%(levelname)s] [%(filename)s] [%(lineno)d]: %(message)s"
            }},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "extend",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "filename": f"{log_file_path}/buybot.log",
                "maxBytes": 100000,
                "formatter": "extend"
            }
        },
        "loggers": {
            "buy-bot": {
                "level": "DEBUG",
                "handlers": [
                    "console", "file"
                ]
            }
        }
    }
    os.makedirs(log_file_path, exist_ok=True)
    logging.config.dictConfig(log_config)
