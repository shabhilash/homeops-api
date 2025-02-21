from sqlalchemy.orm import Session
from app.database import Config, SessionLocal
from sqlalchemy.exc import SQLAlchemyError


def get_config_value(key: str, db: Session = None):
    """
    Universal function to get configuration values based on the key.
    Args:
        key (str): The configuration key to look for.
        db (Session): Optional database session. If not provided, a temporary session is used.
    Returns:
        str: The configuration value.
    Raises:
        ValueError: If the key is not found or there's a database error.
    """
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        config_value = db.query(Config.value).filter(key == Config.key).scalar()

        if config_value is None:
            raise ValueError(f"Configuration for key '{key}' not found.")

        return config_value
    except Exception as e:
        raise ValueError(f"Error fetching config for key '{key}': {str(e)}")
    finally:
        if own_session:
            db.close()


def set_config_value(key: str, value: str, db: Session = None) -> None:
    """
    Universal function to set/update configuration values.
    Creates new entry if key doesn't exist, updates existing one if it does.

    Args:
        key (str): Configuration key
        value (str): Configuration value
        db (Session): Optional database session (will create temporary if not provided)

    Raises:
        ValueError: On database errors
    """
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        # Check if key exists
        config_entry = db.query(Config).filter(key == Config.key).first()

        if config_entry:
            # Update existing entry
            config_entry.value = value
        else:
            # Create new entry
            new_entry = Config(key=key, value=value)
            db.add(new_entry)

        # Only commit if we own the session
        if own_session:
            db.commit()

    except SQLAlchemyError as e:
        if own_session:
            db.rollback()
        raise ValueError(f"Error setting config for key '{key}': {str(e)}")
    finally:
        if own_session:
            db.close()