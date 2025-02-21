from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound

from app.core.logger import logger
from app.database import Config, engine, test_db_connection


# Merged function to check and run initial setup, including loading default configs
def database_initial_setup():
    """Check the config table for 'FIRST_RUN', run the initial DB setup, and insert default configs if necessary."""
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Query for the 'FIRST_RUN' row in the config table
        setup_flag = session.query(Config).filter_by(key="FIRST_RUN").one()

        if setup_flag.value is False:
            # If the 'FIRST_RUN' value is False, run the initial DB setup
            logger.info("Running initial database setup...")
            test_db_connection()  # Run your database setup function

            # Insert default configurations
            load_default_configs(session)

            # Update 'FIRST_RUN' flag to True to prevent further runs
            setup_flag.value = True
            session.commit()
            logger.info("Database setup complete. 'FIRST_RUN' flag set to True.")
        else:
            logger.debug("Database setup already completed. Skipping setup.")

    except NoResultFound:
        # If the 'FIRST_RUN' row does not exist, create it and run the setup
        logger.info("No 'FIRST_RUN' flag found, creating new row and running setup...")
        test_db_connection()  # Run the setup

        # Create the 'FIRST_RUN' row with False value (since it's the first time setup)
        new_setup_flag = Config(key="FIRST_RUN", value=True)
        session.add(new_setup_flag)
        session.commit()
        logger.info("Database setup complete. 'FIRST_RUN' flag created and set to True.")

        # Insert default configurations
        load_default_configs(session)

    finally:
        session.close()


# Helper function to load default configurations
def load_default_configs(session):
    """Load default configuration values into the config table if they don't already exist."""
    try:
        default_configs = {
            "API_URL": "https://localhost:8000",
            "ENVIRONMENT": "PROD",
            "REQUEST_LIMIT": 2,
            "TIME_WINDOW": 1,
            "API_KEY": "my-api-key",
            "ADMIN_API_KEY": "admin-api-key",
        }

        existing_keys = {config.key for config in session.query(Config.key).all()}

        # Prepare new configurations to be inserted
        new_configs = [
            Config(key=key, value=value)
            for key, value in default_configs.items()
            if key not in existing_keys
        ]

        if new_configs:
            session.add_all(new_configs)
            session.commit()
            logger.info(f"Inserted {len(new_configs)} new default configs.")
        else:
            logger.info("All default configs already exist, skipping insertion.")

    except Exception as e:
        session.rollback()
        logger.info(f"Error inserting default configs: {e}")


database_initial_setup()