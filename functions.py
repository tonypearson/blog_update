# functions.py
# Funtions that can be used by other modulues
# Tony Pearson, IBM, July 2020
#
# To include these functions, use:
#
#    from functions import get_modname, setup_logging
#

import datetime
import logging
import re


def get_modname(argv):
    """ get the module name without the .py ending """
    # Determine this module's name
    modname = argv[0]
    modname = re.sub(r'[./]{0,2}([-_a-z0-9]*)\.(.*)$', r'\1', modname)
    return modname


def setup_logging(name, module):
    """ Setup logging level, filename and format of log entries """
    today = datetime.datetime.now()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Change to DEBUG for detail information
    logname = '{}-{}.log'.format(today.strftime("%m-%d"), module)
    file_handler = logging.FileHandler(logname)
    formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s",
                                  "%H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
