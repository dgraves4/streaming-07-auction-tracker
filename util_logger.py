"""
======================= INSTRUCTOR-GENERATED FILE =============================
Source: https://github.com/denisecase/nw-diagnostics-python/
================================================================================

PURPOSE: 
- This logger automatically records your work to a file and the console, 
  eliminating the need to manually copy-paste terminal output. 

NO WORRIES:
- This is NOT part of your project tasks. It's here to help.
- As an instructor-provided script, there's no need to modify or delve 
  into its internals. 
- Logging is a common professional practice. Most major projects use logging. 

NO EXTERNAL DEPENDENCIES:
- This script uses ONLY modules included in the Python standard library.
- No installations (besides Python) are required.

USAGE:
- Add this file to your repository. 
- In the file you want to log, add the following near the top.

  from util_logger import setup_logger
  logger, logname = setup_logger(__file__)

In your code file, instead of print(), use logger.info().

  logger.info(f"Name: {name} ")

Levels include: debug, info, warning, error, and critical.

@Author: Denise Case
@Updated: 2021-08

==========================================================================
"""

# Import some helpful modules from the Python Standard Library

import logging
import pathlib
import platform
import sys
import os
import datetime

# Declare constants (typically constants are named with ALL_CAPS)

DIVIDER = "=" * 50  # A string divider for cleaner output formatting

# Define program functions (reusable bits of code)


def setup_logger(current_file):
    """
    Setup a logger to automatically record useful information.
    @param current_file: the name of the file requesting a logger.
    @returns: the logger object and the name of the logfile.
    """
    logs_dir = pathlib.Path("logs")
    logs_dir.mkdir(exist_ok=True)

    module_name = pathlib.Path(current_file).stem
    log_file_name = logs_dir.joinpath(module_name + ".log")

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)  # Set the root logger level.

    # Create file handler to write logging messages to a file
    file_handler = logging.FileHandler(log_file_name, "w")
    file_handler.setLevel(logging.DEBUG)

    # Create console handler to write logging messages to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter and add it to the handlers.
    formatter = logging.Formatter("%(asctime)s.%(name)s.%(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger.
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    python_version_string = platform.python_version()
    today = datetime.date.today()

    logger.info(f"{DIVIDER}")
    logger.info(f"Today is {today} at {datetime.datetime.now().strftime('%I:%M %p')}")
    logger.info(f"Running on: {os.name} {platform.system()} {platform.release()}")
    logger.info(f"Python version:  {python_version_string}")
    logger.info(f"Python path: {sys.prefix}")
    logger.info(f"Working dir: {os.getcwd()}")
    logger.info(f"{DIVIDER}")

    return logger, log_file_name
