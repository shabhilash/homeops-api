import logging.config
import os

# Get the absolute path of the root folder
current_folder = os.path.dirname(os.path.abspath(__file__))
app_folder = os.path.join(current_folder,"..")

# Function to check if a subdirectory exists
def check_sub_dir_exists(sub_dir):
    # print(f"INFO: {sub_dir} - Checking if the subdir exists.")
    sub_folder = os.path.join(app_folder, sub_dir)

    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)  # Create the folder if it doesn't exist
        print(f"INFO: {sub_dir} directory created.")
    else:
        # print(f"INFO: {sub_dir} directory already exists.")
        pass


# Function to set up the logger
def setup_logger():
    # Ensure the 'logs' folder exists before setting up the logger
    check_sub_dir_exists("logs")

    # Correct path to the logging config file (adjusted for your folder structure)
    config_file = os.path.join(current_folder, 'settings.ini')

    # Ensure the logging config file exists
    if not os.path.exists(config_file):
        print(f"ERROR: Configuration file '{config_file}' not found.")
        return None

    # Load logging configuration from the settings.ini file
    logging.config.fileConfig(config_file, disable_existing_loggers=False)

    # Create and configure the logger
    root_logger = logging.getLogger('homeops')

    # Log an info message to confirm logger setup
    root_logger.debug(f"Logger initialized using config file: {config_file}")

    return root_logger


# Set up the logger and make it available globally
logger = setup_logger()
CONFIGFILE = os.path.join(os.path.dirname(__file__), 'settings.ini')