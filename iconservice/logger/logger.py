# Copyright [theloop]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import json
from .configuration import LogConfiguration, LogHandlerType
from enum import IntEnum

DEFAULT_LOG_FORMAT = "%(asctime)s %(process)d %(thread)d [TAG] %(levelname)s %(message)s"
DEFAULT_LOG_FILE_PATH = "./logger.log"


class LogLevel(IntEnum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class Logger:
    def __init__(self, import_file_path: str = None):
        if import_file_path is None:
            self.__log_preset = self.make_default_preset()
        else:
            self.__log_preset = self.import_file(import_file_path)
        self.update_other_logger_level('pika')
        self.update_other_logger_level('aio_pika')
        self.update_other_logger_level('sanic.access')

    def import_file(self, path: str):
        try:
            with open(path) as f:
                conf = json.load(f)
                logger_config = conf["logger"]
                log_format = logger_config.get("logFormat", DEFAULT_LOG_FORMAT)
                log_level = logger_config.get("logLevel", LogLevel.DEBUG)
                log_color = logger_config.get("colorLog", True)
                log_output = logger_config.get('logFilePath', DEFAULT_LOG_FILE_PATH)
                log_output_type_str = logger_config.get('logOutputType', 'debug')
                preset = LogConfiguration()
                preset.log_format = log_format
                preset.log_level = log_level
                preset.log_color = log_color
                preset.log_file_path = log_output
                preset.set_handler(LogHandlerType[log_output_type_str])
                return preset
        except Exception:
            return self.make_default_preset()

    def make_default_preset(self):
        preset = LogConfiguration()
        preset.log_format = DEFAULT_LOG_FORMAT
        preset.log_level = LogLevel.DEBUG
        preset.log_color = True
        preset.log_file_path = DEFAULT_LOG_FILE_PATH
        preset.set_handler(LogHandlerType.production)
        return preset

    def update_other_logger_level(self, logger_name: str):
        logger = logging.getLogger(logger_name)
        if logger is not None:
            self.__log_preset.update_logger(logger)

    def set_log_level(self, log_level: 'LogLevel'):
        self.__log_preset.log_level = log_level
        self.__log_preset.update_logger()

    def set_handler_type(self, handler_type: 'LogHandlerType'):
        self.__log_preset.set_handler(handler_type)
        self.__log_preset.update_logger()

    @staticmethod
    def info(msg: str, tag: str = 'LOG'):
        logging.info(Logger.__make_log_msg(msg, tag))

    @staticmethod
    def debug(msg: str, tag: str = 'LOG'):
        logging.debug(Logger.__make_log_msg(msg, tag))

    @staticmethod
    def warning(msg: str, tag: str = 'LOG'):
        logging.warning(Logger.__make_log_msg(msg, tag))

    @staticmethod
    def exception(msg, tag: str = 'LOG'):
        logging.exception(Logger.__make_log_msg(msg, tag), exc_info=True)

    @staticmethod
    def error(msg: str, tag: str = 'LOG'):
        logging.error(Logger.__make_log_msg(msg, tag))

    @staticmethod
    def __make_log_msg(msg: str, tag: str):
        return f'[{tag}]{msg}'