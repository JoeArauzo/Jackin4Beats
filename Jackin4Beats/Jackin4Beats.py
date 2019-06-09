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
import shutil
from pydub import AudioSegment
from send2trash import send2trash
import re
import taglib


def detect_leading_silence(sound, silence_threshold, chunk_size=1):
    logger = logging.getLogger(__name__)
    counter_ms = 0
    sound_length = len(sound) - 1
    
    while True:
        level = sound[counter_ms:counter_ms+chunk_size].dBFS
        # logger.debug(f"Level: {level} at " +
        #              f"{str(timedelta(milliseconds=counter_ms))[:-3]}")
        if level > silence_threshold or counter_ms == sound_length:
            break
        counter_ms += chunk_size

    if counter_ms == sound_length:
        counter_ms = 0
    
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
@click.option('--verbose', 'verbosity', flag_value='verbose',
              help='Verbose output')
@click.option('--debug', 'verbosity', flag_value='debug',
              help='Debug output')
def trim_audiosilence(file, verbosity, test, end_offset, begin_offset,
                      threshold):
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
        logger.error(f"The file '{audiofile}' does not exist.")
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
    tmp_name = f"{start_time:%Y%m%dT%H%M%S%f}"
    audiofile_ext = audiofile.suffix.lower()[1:]
    supported_extensions = ('aiff', 'aif')
    tmp_audiofile1 = audiofile.parent / tmp_name / audiofile.name
    tmp_audiofile2 = tmp_name + audiofile.suffix
    tmp_audiofile2 = audiofile.parent / tmp_name / tmp_audiofile2

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
    logger.info(f"File to trim               :  {audiofile}")
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
    
    # Set trimmed audio segment
    trimmed_sound = sound[start_trim:duration_ms-end_trim]

    # Display addt'l info
    logger.info(f"Start trim w/ offset       :  " +
                f"{str(timedelta(milliseconds=start_trim))[:-3]}") 
    logger.info(f"End trim w/ offset         :  " +
                f"{str(timedelta(milliseconds=end_trim))[:-3]}")

    # Proceed if audio silence detected
    if len(trimmed_sound) != duration_ms:
        logger.info("New duration (h:m:s.ms)    :  " +
                f"{str(timedelta(milliseconds=len(trimmed_sound)))[:-3]}")
        # Perform trim process if test flag not set
        if not test:
            logger.debug(f"Opening '{audiofile}' to inspect metadata.")
            try:
                metadata = taglib.File(str(audiofile))
            except:
                logger.error("Unable to inspect audio metadata.")
                sys.exit()
            # Backup ID3 tags if detected
            if len(metadata.tags):

                # Set ID3 TRACKNUMBER to 1 if value is null
                if ( (not 'TRACKNUMBER' in metadata.tags) or
                        (not len(metadata.tags["TRACKNUMBER"])) ):
                    metadata.tags["TRACKNUMBER"] = ["1"]
                    logger.debug("ID3 TRACKNUMBER missing.  Setting to '1'.")
                    try:
                        metadata.save()
                    except:
                        logger.error("Unable to set ID3 TRACKNUMBER.")
                        sys.exit()

                # Copy file to temp working directory
                logger.debug("Creating temp working directory at " +
                             f"'{tmp_audiofile1.parent}'.")
                try:
                    tmp_audiofile1.parent.mkdir(parents=True)
                except:
                    logger.error("Unable to create temp working directory.")
                    sys.exit()
                logger.debug(f"Opening '{audiofile}' to inspect metadata.")
                try:
                    shutil.copy2(audiofile, tmp_audiofile1.parent)
                except IOError as e:
                    logger.error(f"Unable to copy file. {e}")
                    sys.exit()

                # Upgrade metadata to ID3v2.4
                logger.debug("Upgrading metadata to ID3v2.4.")
                kid3_cmd = "to24"
                try:
                    sh.kid3_cli("-c", kid3_cmd, "-c", "save", tmp_audiofile1)
                except Exception as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to upgrade metadata to ID3v2.4.")
                    sys.exit()
                
                # Clear value for encoded-by
                logger.debug("Clearing value of ENCODEDBY.")
                kid3_cmd = "set encoded-by '' 2"
                try:
                    sh.kid3_cli("-c", kid3_cmd, "-c", "save", tmp_audiofile1)
                except Exception as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to clear value of ENCODEDBY.")
                    sys.exit()
                
                # Backup ID3 tag info
                logger.debug(f"Exporting ID3 tags to '{tmp_audiofile1}'.")
                metadata_bak = "metadata.csv"
                metadata_bak = tmp_audiofile1.parent / metadata_bak
                kid3_cmd = f"export '{metadata_bak}' 'CSV unquoted' 2"
                try:
                    sh.kid3_cli("-c", kid3_cmd, tmp_audiofile1)
                except Exception as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to export tags.")
                    sys.exit()
                
                # Export cover art
                logger.debug(f"Exporting image.")
                img_bak = "image.jpg"
                img_bak = tmp_audiofile1.parent / img_bak
                kid3_cmd = f"get picture:'{img_bak}'"
                try:
                    sh.kid3_cli("-c", kid3_cmd, tmp_audiofile1)
                except Exception as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to export image.")
                    sys.exit()

                sys.exit()

            logger.debug("Attempting to export trimmed file as " +
                        f"'{tmp_audiofile2.name}'.")
            try:
                trimmed_sound.export(tmp_audiofile, format='aiff')
                logger.debug("Export successful.")
            except:
                logger.error("Problem exporting temp file.")
                sys.exit(6)
            
            try:
                send2trash(str(audiofile))
                logger.debug("Original file successfully sent to trash.")
            except:
                logger.error("Problem sending original file to trash.")
                sys.exit(7)

            try:
                Path(tmp_audiofile).rename(audiofile)
                logger.debug("Successfuly renamed temp file as original file.")
            except:
                logger.error("Problem renaming temp file as original file.")
                sys.exit(8)

            logger.info("File successfully trimmed.")
        else:
            logger.info("--test flag enabled.  Original file will remain " +
                        "intact.")
    
    else:
        logger.info("No audio silence detected.  Nothing to trim.")
    
    logger.debug("Process completed in      :  " +
                 f"{datetime.now() - start_time}")
    click.echo("Done.")


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

def main():
    click.echo('TRIM-AUDIOSILENCE')
    click.echo('--------------------')
    print_help_msg(trim_audiosilence)