"""
Usage::
        from Detector.UtilsLogging import logging, DICT_NAME_TO_LEVEL, STR_LEVEL_NAMES, init_logger
        logger = logging.getLogger(__name__)
        init_logger(loglevel='DEBUG', logfname=None)
        logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d %(filename)s %(message)s', level=logging.INFO)
        logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d %(message)s', level=logging.INFO)
"""
import logging
logger = logging.getLogger(__name__)

import sys
PYTHON_VERSION_MAJOR = sys.version_info.major  # (int) 2 or 3
DICT_NAME_TO_LEVEL = logging._nameToLevel if PYTHON_VERSION_MAJOR == 3 else\
                     {k:v for k,v in logging._levelNames.items() if isinstance(k, str)} if PYTHON_VERSION_MAJOR == 2 else\
                     {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'WARN': 30,\
                      'ERROR': 40, 'FATAL': 50,'CRITICAL': 50}
STR_LEVEL_NAMES = ', '.join(DICT_NAME_TO_LEVEL.keys())


def basic_config(format='[%(levelname).1s] L%(lineno)04d: %(filename)s %(message)s', int_loglevel=None, str_loglevel='INFO'):
    loglevel = int_loglevel if int_loglevel is not None else DICT_NAME_TO_LEVEL[str_loglevel]
    logging.basicConfig(format=format, level=loglevel)


def init_logger(loglevel='DEBUG', logfname=None, fmt=None):

    int_loglevel = DICT_NAME_TO_LEVEL[loglevel.upper()]

    logger = logging.getLogger()
    logger.setLevel(int_loglevel) # logging.DEBUG
    fmt = fmt if fmt is not None else\
          '[%(levelname).1s] %(filename)s L%(lineno)04d %(message)s' if int_loglevel==logging.DEBUG else\
          '[%(levelname).1s] L%(lineno)04d %(message)s'
    formatter = logging.Formatter(fmt)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(int_loglevel)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if logfname is not None:
        file_handler = logging.FileHandler(logfname) #'log-in-file-test.log'
        file_handler.setLevel(int_loglevel) # logging.DEBUG
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

# EOF
