# -*- coding: utf-8 -*-


"""Jackin4Beats.myfunctions: myutils module within the Jackin4Beats package."""


import sys
import logging
from pathlib import Path

def initcflogger(name, level, rdnn, app_name, supported_platforms):
    """This function sets up console & file logging and returns a logger object."""

    # Set log name equal to script name with .log extension
    log_name = app_name + '.log'
    
    if (sys.platform in supported_platforms):

        # Check if running macOS
        if (sys.platform == 'darwin'):
            log_path = '~/library/logs'
            p = Path(log_path)
            log_path = p.expanduser()
            log_path = log_path / rdnn / log_name
            if not log_path.parent.exists():
                log_path.parent.mkdir(parents=True)

    else:
        sys.exit("Your OS is not supported for logging to a file.")
    
    # Create a customer logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_path)
    if level == 'INFO':
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)
    elif level == 'DEBUG':
        c_handler.setLevel(logging.DEBUG)
        f_handler.setLevel(logging.DEBUG)
    else:
        c_handler.setLevel(logging.ERROR)
        f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_formatter = logging.Formatter('%(levelname)5s: %(message)s')
    f_formatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(name)s] %(message)s')
    c_handler.setFormatter(c_formatter)
    f_handler.setFormatter(f_formatter)

    # # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

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