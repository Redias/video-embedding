#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
from logging import Filter


class MyFilter(Filter):
    def filter(self, record):
        # record.__dict__.update(
        #     task_name='',
        # )
        return True


def filter_maker(level):
    level = getattr(logging, level)

    def filter(record):
        return record.levelno <= level

    return filter
