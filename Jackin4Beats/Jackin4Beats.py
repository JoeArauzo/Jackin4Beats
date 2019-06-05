# -*- coding: utf-8 -*-


"""Jackin4Beats.Jackin4Beats: provides entry point main()."""


__version__ = "0.1.0"


import click
from .myfunctions import initclogger
from pathlib import Path
from datetime import datetime
import sh
import sys
import re
from .myfunctions import pathwoconflict
import os


@click.command()
@click.argument('file')
@click.option('--threshold', '-t', metavar='<dB>', default=-96.0, type=float)
@click.option('--begin_offset', '-b', metavar='<ms>', default=0, type=int)
@click.option('--end_offset', '-e', metavar='<ms>', default=0, type=int)
@click.option('--test', is_flag=True, help='Perform test run without making changes')
@click.option('--verbose', '-v', is_flag=True, help="Verbose output")
def trim_audiosilence(file, verbose, test, end_offset, begin_offset, threshold):
    """
    This command-line tool removes leading and trailing silence from an AIFF
    audio file.
    """
    
    
    # Initialize logging and begin
    if verbose:
        logger = initclogger(__name__, 'INFO')
    else:
        logger = initclogger(__name__, 'ERROR')
    logger.info(f"Executing TRIM-AUDIOSILENCE version {__version__}.")

    # Exit if file does not exist
    audiofile = Path(file).resolve()
    if not audiofile.is_file():
        logger.error(f"The file '{audiofile.name}' does not exist.")
        sys.exit(1)
    
    # Exit if kid3-cli is not accessible
    if not sh.which('kid3-cli'):
        logger.error("The dependency, KID3-CLI, is not accessible.  Please" +
                     "install or check the PATH.")
        sys.exit(2)

    #  


    # 




def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

def main():
    click.echo('TRIM-AUDIOSILENCE')
    click.echo('--------------------')
    print_help_msg(trim_audiosilence)