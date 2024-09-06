#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger as loguru_logger

load_dotenv()


class CustomLogger:
    def __init__(self, log_directory: str, rotation_interval: timedelta = timedelta(minutes=15),
                 retention_days: int = 7, file_name: str = 'app.log', console_level: str = 'INFO'):
        self.log_directory = Path(log_directory)
        self.rotation_interval = rotation_interval
        self.retention_days = retention_days
        self.file_name = file_name
        self.console_level = console_level

        # Ensure the log directory exists
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Setup Loguru logger
        self.setup_logger()

    def setup_logger(self):
        log_file_path = self.log_directory / self.file_name
        loguru_logger.remove()
        loguru_logger.add(
            log_file_path,
            rotation=self.rotation_interval,
            retention=timedelta(days=self.retention_days),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="DEBUG",
            enqueue=True  # Ensure logs are written in a thread-safe manner
        )
        loguru_logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level=self.console_level
        )
        error_log_file_path = self.log_directory / 'error.log'
        loguru_logger.add(
            error_log_file_path,
            rotation="500 MB",  # Rotate when file size exceeds 500 MB
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )

    @staticmethod
    def debug(message: str, **kwargs):
        loguru_logger.debug(message, **kwargs)

    @staticmethod
    def info(message: str, **kwargs):
        loguru_logger.info(message, **kwargs)

    @staticmethod
    def warning(message: str, **kwargs):
        loguru_logger.warning(message, **kwargs)

    @staticmethod
    def error(message: str, **kwargs):
        loguru_logger.error(message, **kwargs)

    @staticmethod
    def exception(message: str, **kwargs):
        loguru_logger.exception(message, **kwargs)

    @staticmethod
    def critical(message: str, **kwargs):
        loguru_logger.critical(message, **kwargs)


def initialize_logging(filename=None, console_level=None,
                       rotation_interval=None, retention_days=None):
    if rotation_interval is None:
        rotation_interval = int(os.getenv('LOG_ROTATION_IN_MINS', 15))
    if retention_days is None:
        retention_days = int(os.getenv('LOG_RETENTION', 7))
    if console_level is None:
        console_level = os.getenv('LOG_CONSOLE_LEVEL', 'INFO')
    if filename is None:
        filename = os.getenv('APP_NAME', 'MBSR-TASK')
    return CustomLogger(
        os.getenv('LOG_DIR', r'D:\mbsr-reports\test-data\logs'),
        rotation_interval=timedelta(minutes=rotation_interval),
        retention_days=retention_days,
        file_name=f'{filename}.log',
        console_level=console_level
    )
