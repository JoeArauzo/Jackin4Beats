# -*- coding: utf-8 -*-


"""Jackin4Beats.Jackin4Beats: provides entry point main()."""


__version__ = "0.1.0"
RDNN = 'net.arauzo.utils'
SUPPORTED_PLATFORMS = ['darwin']


import logging
import click
from .myfunctions import initcflogger
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
import time


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
@click.argument("file")
@click.option("--metadata", "-m", default="Grouping", metavar="<field>",
              help="The metadata field to write the source material info to, " +
              "e.g. 'Composer' or 'Comments' or 'Description'.  (default: " +
              "'Grouping')")
@click.option("--format", "-f", metavar="<type>",
              help="Format of source material, i.e. 'FLAC', 'AAC', 'MP3', " +
              " etc..  (default: from FILE)")
@click.option("--bitrate", "-b", metavar="<Kbps>",
              help="Bit Rate of source material, i.e. '1411'.  (default: " +
              "from FILE)")
@click.option("--samplingrate", "-s", metavar="<KHz>",
              help="Sampling Rate of source material, i.e. '44.1', '48', " +
              "'96'.  (default: from FILE)")
@click.option("--bitdepth", "-d", metavar="<bits>",
              help="Bit Depth of source material, i.e. '16', '24'.  (default:" +
              " from FILE)")
@click.option("--channels", "-c", metavar="<channels>",
              help="Number of Channels of source material, i.e. '2'.  " +
              "(default: from FILE)")
@click.option("--test", is_flag=True,
              help="Perform test run without making changes")
@click.option("--verbose", "verbosity", flag_value="verbose",
              help="Verbose output")
@click.option("--debug", "verbosity", flag_value="debug",
              help="Debug output")
def write_sourceinfo(file, metadata, format, bitrate, samplingrate, 
                     bitdepth, channels, test, verbosity):
    """
    This CLI tool writes source material information to the 'Grouping' metadata 
    field of the FILE specificed.  For example 'Source: AIFF, 1,411 Kbps,
    44.1 KHz, 2 channels'.
    """ 

    # Initialize logging
    if verbosity == 'verbose':
        logger = initcflogger(__name__, 'INFO', RDNN, 'write-sourceinfo',
                              SUPPORTED_PLATFORMS)
    elif verbosity == 'debug':
        logger = initcflogger(__name__, 'DEBUG', RDNN, 'write-sourceinfo',
                              SUPPORTED_PLATFORMS)
    else:
        logger = initcflogger(__name__, 'ERROR', RDNN, 'write-sourceinfo',
                              SUPPORTED_PLATFORMS)
    logger.info(f"Executing WRITE-SOURCEINFO version {__version__}.")

    # Exit if file does not exist
    audiofile = Path(file).resolve()
    if not audiofile.is_file():
        logger.error(f"The file '{audiofile}' does not exist.")
        sys.exit(1)# 





@click.command()
@click.argument('file')
@click.option('--threshold', '-t', metavar='<dB>', default=-96.0, type=float,
              help='threshold (default: -96.0 dB)')
@click.option('--begin_offset', '-b', metavar='<ms>', default=0, type=int,
              help='beggining offset (default: 0 ms)')
@click.option('--end_offset', '-e', metavar='<ms>', default=0, type=int,
              help='ending offset (default: 0 ms)')
@click.option('--namefromtag', is_flag=True,
              help="Name trimmed file '{artist} - {title}'")
@click.option('--test', is_flag=True,
              help='Perform test run without making changes')
@click.option('--verbose', 'verbosity', flag_value='verbose',
              help='Verbose output')
@click.option('--debug', 'verbosity', flag_value='debug',
              help='Debug output')
def trim_audiosilence(file, verbosity, namefromtag, test, end_offset, begin_offset,
                      threshold):
    """
    This CLI tool removes leading and trailing silence from an AIFF
    audio file and preserves metadata.
    """
    
    
    # Initialize logging
    if verbosity == 'verbose':
        logger = initcflogger(__name__, 'INFO', RDNN, 'trim-audiosilence',
                              SUPPORTED_PLATFORMS)
    elif verbosity == 'debug':
        logger = initcflogger(__name__, 'DEBUG', RDNN, 'trim-audiosilence',
                              SUPPORTED_PLATFORMS)
    else:
        logger = initcflogger(__name__, 'ERROR', RDNN, 'trim-audiosilence',
                              SUPPORTED_PLATFORMS)
    logger.info(f"Executing TRIM-AUDIOSILENCE version {__version__}.")

    # Exit if file does not exist
    audiofile = Path(file).resolve()
    if not audiofile.is_file():
        logger.error(f"The file '{audiofile}' does not exist.")
        sys.exit(1)
    
    # Dependency checking
    dependencies = {
        'KID3-CLI': 'kid3-cli',
        'FFMPEG': 'ffmpeg',
        'TAGLIB': 'taglib-config'
    }
    for dependency, file in dependencies.items():
        if not shutil.which(file):
            logger.error(f"The dependency, {dependency}, is not accessible. " +
                         " Please install or check the PATH.")
            sys.exit(2)

    # Initialize variables
    import taglib
    kid3_cli = sh.Command("kid3-cli")
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
    logger.debug(f"Opening '{audiofile}' for analysis...")
    try:
        sound = AudioSegment.from_file(audiofile)
    except IOError as e:
        logger.error(f"I/O error({e.errno}) - {e.strerror}: '{audiofile}'")
        sys.exit(5)
    logger.debug("Open successful.")

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
            # Copy file to temp working directory
            logger.debug("Creating temp working directory at " +
                            f"'{tmp_audiofile1.parent}'...")
            try:
                tmp_audiofile1.parent.mkdir(parents=True)
            except:
                logger.error("Unable to create temp working directory.")
                sys.exit()
            logger.debug("Temp working directory created successfully.")
            logger.debug("Copying file to temp working directory...")
            try:
                shutil.copy2(audiofile, tmp_audiofile1.parent)
            except IOError as e:
                logger.error(f"Unable to copy file. {e}")
                sys.exit()
            logger.debug("Copy successful.")
            
            # Inspect metadata
            logger.debug(f"Opening '{tmp_audiofile1}' to acquire metadata...")
            try:
                metadata = taglib.File(str(tmp_audiofile1))
            except:
                logger.error("Unable to acquire audio metadata.")
                sys.exit()
            logger.debug("Metadata acquired successfully.")
            
            # Backup ID3 tags if detected
            if len(metadata.tags):

                # Set ID3 TRACKNUMBER to 1 if value is null
                if ( (not 'TRACKNUMBER' in metadata.tags) or
                        (not len(metadata.tags["TRACKNUMBER"])) ):
                    metadata.tags["TRACKNUMBER"] = ["1"]
                    logger.debug("ID3 TRACKNUMBER missing.  Setting to value " +
                                 "'1'...")
                    try:
                        metadata.save()
                    except:
                        logger.error("Unable to set ID3 TRACKNUMBER.")
                        sys.exit()
                    logger.debug("Value set successfully.")

                # Clear value for ENODEDBY
                logger.debug("Clearing value of ENCODEDBY...")
                kid3_cmd = "set encoded-by '' 2"
                try:
                    kid3_cli("-c", kid3_cmd, "-c", "save", tmp_audiofile1)
                except sh.ErrorReturnCode as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to clear value of ENCODEDBY.")
                    sys.exit()
                logger.debug("Value cleared successfully.")
                
                # Backup metadata
                metadata_bak = "metadata.csv"
                metadata_bak = tmp_audiofile1.parent / metadata_bak
                logger.debug(f"Exporting metadata to '{metadata_bak}'...")
                kid3_cmd = f"export '{metadata_bak}' 'CSV unquoted' 2"
                try:
                    kid3_cli("-c", kid3_cmd, tmp_audiofile1)
                except sh.ErrorReturnCode as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to export tags.")
                    sys.exit()
                logger.debug("Export successful.")
                
                # Export album artwork
                logger.debug(f"Exporting album artwork...")
                img_bak = "artwork.jpg"
                img_bak = tmp_audiofile1.parent / img_bak
                kid3_cmd = f"get picture:'{img_bak}'"
                try:
                    kid3_cli("-c", kid3_cmd, tmp_audiofile1)
                except sh.ErrorReturnCode as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to export album artwork.")
                    sys.exit()
                logger.debug("Export successful.")

            # Save trimmed audio file
            os.remove(tmp_audiofile1)
            logger.debug(f"Saving trimmed audio file as '{tmp_audiofile1}'...")
            try:
                trimmed_sound.export(tmp_audiofile1, format='aiff')
            except:
                logger.error("Problem saving trimmed audio file.")
                sys.exit(6)
            logger.debug("Save successful.")
            
            # Restore metadata to trimmed audio file
            if len(metadata.tags):
                logger.debug(f"Restoring metadata...")
                kid3_cmd = f"import '{metadata_bak}' 'CSV unquoted' 2"
                try:
                    kid3_cli("-c", kid3_cmd, "-c", "save", tmp_audiofile1)
                except sh.ErrorReturnCode as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to restore metadata.")
                    sys.exit()
                logger.debug("Restore successful.")

                # Restore album artwork
                logger.debug(f"Restoring album artwork...")
                kid3_cmd = f"set picture:'{img_bak}' 2"
                try:
                    kid3_cli("-c", kid3_cmd, "-c", "save", tmp_audiofile1)
                except sh.ErrorReturnCode as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to restore album artwork.")
                    sys.exit()
                logger.debug("Restore successful.")
            
            # Send original file to trash
            try:
                send2trash(str(audiofile))
                logger.debug("Original file successfully sent to trash.")
            except:
                logger.error("Problem sending original file to trash.")
                sys.exit(7)

            # Replace original file with trimmed version
            logger.debug("Renaming temp file as original file...")
            try:
                Path(tmp_audiofile1).rename(audiofile)
            except:
                logger.error("Problem renaming temp file as original file.")
                sys.exit(8)
            logger.debug("Successfuly renamed temp file as original file.")

            # Delete temp working directory
            logger.debug("Deleting temp working directory...")
            try:
                shutil.rmtree(tmp_audiofile1.parent)
            except IOError as e:
                logger.error(f"Unable to delete temp working directory. {e}")
                sys.exit()
            logger.debug("Delete successful.")

            if len(metadata.tags) and namefromtag: 
                # Rename trimmed file from tags
                logger.debug("Renaming trimmed file as {artist} - {title}...")
                kid3_cmd = "fromtag '%{artist} - %{title}' 2"
                try:
                    kid3_cli("-c", kid3_cmd, audiofile)
                except sh.ErrorReturnCode as e:
                    logger.debug(f"RAN: {e.full_cmd}")
                    logger.debug(f"STDOUT: {e.stdout}")
                    logger.debug(f"STDERR: {e.stderr}")
                    logger.error("Unable to rename trimmed file.")
                    sys.exit()
                logger.debug("Rename successful.")

            logger.info("File successfully trimmed.")
        
        else:
            logger.info("--test flag enabled.  Original file will remain " +
                        "intact.")
    
    else:
        logger.info("No audio silence detected.  Nothing to trim.")
    
    logger.debug(f"Process completed in {datetime.now() - start_time}")
    click.echo("Done.")


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

def main():
    click.echo('TRIM-AUDIOSILENCE')
    click.echo('--------------------')
    print_help_msg(trim_audiosilence)
    click.echo('\n\n')
    click.echo('WRITE-SOURCEINFO')
    click.echo('--------------------')
    print_help_msg(write_sourceinfo)