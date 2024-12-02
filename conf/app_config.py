# config.py

import configparser

from conf import log_config

# Load general settings from autolab.ini
configFile = "autolab.ini"
config = configparser.ConfigParser()
config.read(configFile)

# The logger is set up and available globally
logger = log_config.logger

# Example: Database URL and app configurations
# debug_mode = config['log']['RootLogLevel']
# These configurations are available for the rest of your application
DB_NAME = config['database']['DatabaseName']+".db"