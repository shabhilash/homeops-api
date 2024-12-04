import configparser
import os
import sqlite3
from conf import log_config
from conf.log_config import check_sub_dir_exists

current_folder = os.path.dirname(os.path.abspath(__file__))
app_folder = os.path.join(current_folder,"..")

check_sub_dir_exists("db")
db_folder = os.path.join(app_folder, "db")

# Load config from settings.ini
configFile  = os.path.join(os.path.dirname(__file__), 'settings.ini')
config = configparser.ConfigParser()
config.read(configFile)

# The logger is set up and available globally
logger = log_config.logger

#####################################################################
# These configurations are available for the rest of your application
#####################################################################
DB_NAME = config['database']['DatabaseName']+".db"
DB_CONN_OPEN = False  # Global flag to track connection state

##########
# TEST ENV
DB_PATH = ":memory:"
DB_CONN = sqlite3.connect(DB_PATH,check_same_thread=False)
##########

##########
# PROD ENV
# DB_PATH = os.path.join(db_folder, DB_NAME)
# DB_CONN = sqlite3.connect(DB_PATH) # PROD ENV
##########