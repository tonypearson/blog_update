from datetime import datetime
import logging
import os
import re
import sys

LOGSDIR = "logs"

class logSystem():
    """ Class to create and manage info/warning/error logs  """

    def __init__(self, argv, level= logging.INFO):
        """ Create logger for this module """
        # Determine this module's name
        modname = argv[0]

        modRegex = r'[./]{0,2}([-_a-z0-9]*)\.(.*)$'
        self.modname = re.sub(modRegex, r'\1', modname)
        self.logger = None
        self.level=level      # Change to DEBUG for detail information
        self.filename = ''
        os.makedirs(LOGSDIR, exist_ok=True)   # store in sub-directory
        self.logmsg = 'Log messages directed to:'
        return None

    def setup(self, name):
        today = datetime.now()
        logger = logging.getLogger(name)
        logger.setLevel(self.level)  
        logname = '{}-{}.log'.format(today.strftime("%m-%d"), self.modname)
        filename = os.path.join(LOGSDIR, logname)
        file_handler = logging.FileHandler(filename)
        formatter = logging.Formatter("%(asctime)s|%(levelname)s|%(message)s",
                                      "%H:%M:%S")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        if self.logmsg:
            print(self.logmsg, filename)
        self.filename = filename
        self.logger = logger
        return logger

    def test_messages(self):
        self.logger.debug('This is a debug message')
        self.logger.info('This is an informational message')
        self.logger.warning('This is a warning message')
        self.logger.error('This is an error message')
        return self

if __name__ == "__main__":
    print('Testing: ', sys.argv[0])

    # Parse input parameters and setup logging-- DEBUG and higher
    debuglog = logSystem(['logtest_debug'], level=logging.DEBUG)
    logger = debuglog.setup('debuglog')
    debuglog.test_messages()

    # Parse input parameters and setup logging -- DEFAULT
    logsys = logSystem(sys.argv)
    logger = logsys.setup(__name__)
    logsys.test_messages()

    # Parse input parameters and setup logging -- WARNING and higher
    warnlog = logSystem(['logtest_warn'], level=logging.WARNING)
    logger = warnlog.setup('warnlog')
    warnlog.test_messages()

    # Parse input parameters and setup logging -- ERROR and higher
    errorlog = logSystem(['logtest_error'], level=logging.ERROR)
    errorlog.logmsg = ''  # Do not announce we are logging messages
    logger = errorlog.setup('errorlog')
    errorlog.test_messages()

    print('Congratulations')
