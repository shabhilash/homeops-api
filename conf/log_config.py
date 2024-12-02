# config/log_config.py

import logging
import logging.config
import os


def setup_logger():
    # Read the config file
    config_file = os.path.join(os.path.dirname(__file__), '..', 'autolab.ini')
    logging.config.fileConfig(config_file, disable_existing_loggers=False)

    # Create and configure the logger
    logger = logging.getLogger('autolab')

    logger.debug(f"Using config file: {config_file}")
    return logger


# Set up the logger and make it available globally
logger = setup_logger()
