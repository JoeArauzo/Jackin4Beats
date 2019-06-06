# -*- coding: utf-8 -*-


"""Jackin4Beats.Jackin4Beats: provides entry point main()."""


__version__ = "0.1.0"


import logging
import click
from .myfunctions import initclogger
from pathlib import Path
from datetime import datetime
from datetime import timedelta
import sh
import sys
import re
from .myfunctions import pathwoconflict
import os
from pydub import AudioSegment


def detect_leading_silence(sound, silence_threshold, chunk_size=1):
    logger = logging.getLogger(__name__)
    counter_ms = 0
    sound_length = len(sound) - 1
    while True:
        level = sound[counter_ms:counter_ms+chunk_size].dBFS
        logger.debug(f"Level: {level} at " +
                     f"{str(timedelta(milliseconds=counter_ms))[:-3]}")
        #print("Level: {} dB at {}".format(level, convert_ms_to_timestring(counter_ms)))
        if level > silence_threshold or counter_ms == sound_length:
            break
        counter_ms += chunk_size

    if counter_ms == sound_length:
        counter_ms = 0
    #print("Returning {} ms".format(convert_ms_to_timestring(counter_ms)))
    return counter_ms


@click.command()
@click.argument('file')
@click.option('--threshold', '-t', metavar='<dB>', default=-96.0, type=float,
              help='threshold (default: -96.0 dB)')
@click.option('--begin_offset', '-b', metavar='<ms>', default=0, type=int,
              help='beggining offset (default: 0 ms)')
@click.option('--end_offset', '-e', metavar='<ms>', default=0, type=int,
              help='ending offset (default: 0 ms)')
@click.option('--test', is_flag=True,
              help='Perform test run without making changes')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def trim_audiosilence(file, verbose, test, end_offset, begin_offset, threshold):
    """
    This command-line tool removes leading and trailing silence from an AIFF
    audio file.
    """
    
    
    # Initialize logging
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
        logger.error("The dependency, KID3-CLI, is not accessible.  Please " +
                     "install or check the PATH.")
        sys.exit(2)
    
    # Exit if ffmpeg is not accessible
    if not sh.which('ffmpeg'):
        logger.error("The dependency, FFMPEG, is not accessible.  Please " +
                     "install or check the PATH.")
        sys.exit(3)

    # Initialize variables
    start_time = datetime.now()
    audiofile_ext = audiofile.suffix.lower()[1:]
    supported_extensions = ('aiff', 'aif')

    # Check if file type is supported by this script
    if not (audiofile_ext in supported_extensions):
        logger.error(f"'{audiofile_ext.upper()}' is not a file type " +
                     "supported by this tool.  'AIFF' is supported.")
        sys.exit(4)

    # Obtain audio segment from file
    try:
        sound = AudioSegment.from_file(audiofile)
    except IOError as e:
        logger.error(f"I/O error({e.errno}) - {e.strerror}: '{audiofile}'")
        sys.exit(5)
    # except:
    #     logger.error(f"Invalid data found when processing '{audiofile.name}'" +
    #                  ".  Please check the file is a valid audio file.")
    #     sys.exit(6) 

    # Display info
    duration_ms = len(sound)
    logger.info(f"File to trim               :  {audiofile.name}")
    logger.info(f"File type                  :  {audiofile_ext.upper()}")
    logger.info(f"Threshold (db)             :  {threshold}")
    logger.info(f"Beginning Offset (ms)      :  {begin_offset}")
    logger.info(f"Ending Offset (ms)         :  {end_offset}")
    logger.info("Duration (h:m:s.ms)        :  " +
                f"{str(timedelta(milliseconds=duration_ms))[:-3]}")

    # Detect silence from beginning and end of audio segment
    start_trim = detect_leading_silence(sound, threshold, chunk_size=1)
    end_trim = detect_leading_silence(sound.reverse(), threshold, chunk_size=1)
    logger.info("Start trim                 :  " +
                f"{str(timedelta(milliseconds=start_trim))[:-3]}")
    logger.info("End trim                   :  " +
                f"{str(timedelta(milliseconds=end_trim))[:-3]}")


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

def main():
    click.echo('TRIM-AUDIOSILENCE')
    click.echo('--------------------')
    print_help_msg(trim_audiosilence)