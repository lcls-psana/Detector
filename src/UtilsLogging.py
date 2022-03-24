"""
Usage::
        from Detector.UtilsLogging import logging, DICT_NAME_TO_LEVEL, STR_LEVEL_NAMES, init_logger
        logger = logging.getLogger(__name__)
        init_logger(loglevel='DEBUG', logfname=None)
"""

import logging
logger = logging.getLogger(__name__)
DICT_NAME_TO_LEVEL = {k:v for k,v in logging._levelNames.iteritems() if isinstance(k, str)}
STR_LEVEL_NAMES = ', '.join(DICT_NAME_TO_LEVEL.keys())

#logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d %(filename)s %(message)s', level=logging.INFO)
#logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d %(message)s', level=logging.INFO)

def init_logger(loglevel='DEBUG', logfname=None, fmt=None):
    import sys

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
