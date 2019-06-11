# -*- coding: utf-8 -*-


"""pyPlexUtils.myfunctions: myutils module within the pyPlexUtils package."""


import logging
from pathlib import Path

def initclogger(name, level):
    """This function sets up console logging and returns a logger object."""

    # Create a customer logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()
    if level == 'INFO':
        c_handler.setLevel(logging.INFO)
    elif level == 'DEBUG':
        c_handler.setLevel(logging.DEBUG)
    else:
        c_handler.setLevel(logging.ERROR)

    # Create formatters and add it to handlers
    c_formatter = logging.Formatter('%(levelname)5s: %(message)s')
    c_handler.setFormatter(c_formatter)

    # # Add handlers to the logger
    logger.addHandler(c_handler)

    return logger


def pathwoconflict(filepath):
    """
    This function inspects the filepath and returns a filepath with a filename
    that will not conflict with any preexisting file.
    """

    filepath = str(filepath)
    filepath = Path(filepath)
    basename = filepath.stem
    c = 1
    while filepath.exists():
        filename = basename + f" {c}" + filepath.suffix
        filepath = filepath.parent / filename
        c += 1
    
    return filepath