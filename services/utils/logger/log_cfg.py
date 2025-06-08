#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os

instance_id = os.getenv("INSTANCE_ID", 0)

# Ensure the log directory exists
log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)


log_cfg = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "custom": {
            "format": "[%(levelname)s]\t%(asctime)s %(filename)s[line:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "custom_filter": {
            "()": "utils.logger.filter.MyFilter",
        },
        "warnings_and_below": {
            "()" : "utils.logger.filter.filter_maker",
            "level": "WARNING"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "custom",
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "custom",
            "stream": "ext://sys.stderr"
        },
        "timed_rotating_file_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "custom",
            "filters": ["custom_filter"],
            "filename": f"./log/Instance_{instance_id}_time.log",
            "when": "MIDNIGHT",  # when * interval 为分隔产生文件
            "interval": 1,
            "backupCount": 2,
            "encoding": "utf8",
        },
        # "size_rotating_file_handler": {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "level": "INFO",
        #     "formatter": "custom",
        #     # "filters": ["custom_filter"],
        #     "filename": f"./log/Instance_{instance_id}_size.log",
        #     "mode": "a", 
        #     "maxBytes": 2048,  # 单位 Bytes, 10 M = 10*1024*1024 Bytes = 1,048,576 Bytes
        #     "backupCount": 3,
        #     "encoding": "utf8",
        # }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "stdout", 
            # "size_rotating_file_handler",
            "timed_rotating_file_handler"
        ],
    }
}
