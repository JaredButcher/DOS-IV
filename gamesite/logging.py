import logging
from typing import Optional

SHORT_FORMAT = logging.Formatter('%(levelname)-8s|%(message)s')
LONG_FORMAT = logging.Formatter('%(asctime)s|%(name)-16s|%(levelname)-8s|%(processName)-8s|%(message)s')

def initLogging(minLevel: Optional[int] = 20, filepath: Optional[str] = None):
    rootLogger = logging.getLogger()
    rootLogger.setLevel(minLevel)

    stdHandler = logging.StreamHandler(stream=sys.stdout)
    stdHandler.setFormatter(SHORT_FORMAT)
    rootLogger.addHandler(stdHandler)

    if not filepath is None:
        fileHandler = logging.FileHandler(filepath)
        fileHandler.setFormatter(LONG_FORMAT)
        rootLogger.addHandler(fileHandler)
 