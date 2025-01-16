import os

import yaml

from app.conf import log_config
from app.conf.log_config import check_sub_dir_exists

current_folder = os.path.dirname(os.path.abspath(__file__))
app_folder = os.path.join(current_folder,"..")

check_sub_dir_exists("database")
db_folder = os.path.join(app_folder, "database")

# Load config from settings.yaml
configFile  = os.path.join(os.path.dirname(__file__), 'settings.yaml')
with open(configFile, 'r') as f:
    config = yaml.safe_load(f)

# The logger is set up and available globally
logger = log_config.logger

#####################################################################
# These configurations are available for the rest of your application
#####################################################################
DB_NAME = config['database']['database']+".db"
DB_CONN_OPEN = False  # Global flag to track connection state

