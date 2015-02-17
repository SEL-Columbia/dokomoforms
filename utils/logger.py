"""
Create a custom logger object for use by the rest of the python logic

"""

import logging
from settings import LOG_LEVEL


def setup_custom_logger(name, level=LOG_LEVEL):
    """Generate the logger object, define the output format,
    and return it to the modules which will use it"""

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
