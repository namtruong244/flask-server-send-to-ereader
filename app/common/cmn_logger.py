import logging
import os
from flask import g
from config.log import log_conf


class CmnLogger:
    LOG_ERROR = 'ERROR'
    LOG_WARNING = 'WARNING'
    LOG_WARN = 'WARN'
    LOG_INFO = 'INFO'
    LOG_DEBUG = 'DEBUG'

    REPLACE_MSG_LOG = (
        ('\r\n', '<0a>'),
        ('\n', '<0a>')
    )

    @staticmethod
    def write_log(log_id, params=None):
        message_log = g.params['MESSAGE_LOG'][log_id]

        msg = message_log['MSG'] % params if '%s' in message_log['MSG'] else message_log['MSG']

        for key, val in CmnLogger.REPLACE_MSG_LOG:
            msg = msg.replace(key, val)

        log_extra = {
            'logcode': message_log['ID']
        }

        level = message_log['LEVEL'].upper()

        match level:
            case CmnLogger.LOG_ERROR:
                logging.error(msg, extra=log_extra)
            case CmnLogger.LOG_WARNING, CmnLogger.LOG_WARN:
                logging.warning(msg, extra=log_extra)
            case CmnLogger.LOG_DEBUG:
                logging.debug(msg, extra=log_extra)
            case CmnLogger.LOG_INFO:
                logging.info(msg, extra=log_extra)

    @staticmethod
    def setup_logging():
        gunicorn_logger = logging.getLogger('gunicorn.error')
        gunicorn_logger.propagate = False

        logger = logging.getLogger()
        logger.handlers = gunicorn_logger.handlers
        formatter = logging.Formatter(log_conf['format'], log_conf['date_fmt'])
        for handler in logger.handlers:
            handler.setFormatter(formatter)

        log_level_conf = os.getenv('LOG_LEVEL').upper()
        match log_level_conf:
            case CmnLogger.LOG_ERROR:
                log_level = logging.ERROR
            case CmnLogger.LOG_WARNING, CmnLogger.LOG_WARN:
                log_level = logging.WARN
            case CmnLogger.LOG_DEBUG:
                log_level = logging.DEBUG
            case CmnLogger.LOG_INFO:
                log_level = logging.INFO
            case _:
                log_level = logging.NOTSET

        logger.setLevel(log_level)
