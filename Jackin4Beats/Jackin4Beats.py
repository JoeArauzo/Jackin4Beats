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
        if level > silence_threshold or counter_ms == sound_length:
            break
        counter_ms += chunk_size

    if counter_ms == sound_length:
        counter_ms = 0
    
    #print("Returning {} ms".format(convert_ms_to_timestring(counter_ms)))
    logger.debug("Found audio at " +
                 f"{str(timedelta(milliseconds=counter_ms))[:-3]}")
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
@click.option('--verbose', 'verbosity', flag_value='verbose', help='Verbose output')
@click.option('--debug', 'verbosity', flag_value='debug', help='Debug output')
def trim_audiosilence(file, verbosity, test, end_offset, begin_offset, threshold):
    """
    This command-line tool removes leading and trailing silence from an AIFF
    audio file.
    """
    
    
    # Initialize logging
    if verbosity == 'verbose':
        logger = initclogger(__name__, 'INFO')
    elif verbosity == 'debug':
        logger = initclogger(__name__, 'DEBUG')
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
    logger.debug('Detecting silence from beginning of audio file.')
    start_trim = detect_leading_silence(sound, threshold, chunk_size=1)
    logger.debug('Detecting silence from end of audio file.')
    end_trim = detect_leading_silence(sound.reverse(), threshold, chunk_size=1)
    logger.info("Start trim                 :  " +
                f"{str(timedelta(milliseconds=start_trim))[:-3]}")
    logger.info("End trim                   :  " +
                f"{str(timedelta(milliseconds=end_trim))[:-3]}")

    # Adjust for user-specified offset from beginning of audio segment
    # Proceed if silence detected at beginning of audio segment
    if start_trim > 0:
        # If negative offset specified
        if begin_offset < 0:
            # Apply offset if silence is long enough
            if start_trim >= abs(begin_offset):
                start_trim -= abs(begin_offset)
        # If positive offset specified
        if begin_offset > 0:
            # Apply offset if audio segment is long enough
            if begin_offset < (duration_ms - (start_trim + end_trim)):
                # Proceed if silence detected at end of audio segment
                if end_trim > 0:
                    # If negative offset specified
                    if end_offset < 0:
                        if begin_offset < (duration_ms - (start_trim + end_trim + abs(end_offset))):
                            start_trim += begin_offset
                else:
                    start_trim += begin_offset

    # Adjust for user-specified offset from end of audio segment
    # Proceed if silence detected
    if end_trim > 0:
        # If positive offset specified
        if end_offset > 0:
            # Apply offset if silence is long enough
            if end_trim >= end_offset:
                end_trim -= end_offset
        # If negative offset specified
        if end_offset < 0:
            if (duration_ms - (end_trim + abs(end_offset))) > start_trim:
                end_trim += abs(end_offset)


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

def main():
    click.echo('TRIM-AUDIOSILENCE')
    click.echo('--------------------')
    print_help_msg(trim_audiosilence)