#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
import logging.config

from .log_cfg import log_cfg


class Logger:
    def __new__(cls):
        logging.config.dictConfig(log_cfg)
        cls.logger = logging.getLogger("stdout")
        return cls.logger
