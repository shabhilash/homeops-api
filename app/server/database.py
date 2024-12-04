import logging
import sqlite3
from fastapi import HTTPException
from conf import app_config

# Logger
logger = logging.getLogger("homeops.db")


async def db_connect():
    if not app_config.DB_CONN_OPEN:
        try:
            app_config.DB_CONN = sqlite3.connect(app_config.DB_PATH)
            app_config.DB_CONN_OPEN = True
            logger.debug("Connected to database")
        except Exception as err:
            logger.error(f"Error connecting to database - {err}")
            app_config.DB_CONN_OPEN = False
    return app_config.DB_CONN_OPEN


async def db_disconnect():
    if app_config.DB_CONN_OPEN and app_config.DB_CONN:
        app_config.DB_CONN.close()
        app_config.DB_CONN_OPEN = False
        logger.debug("Database connection closed.")


async def create_database():
    logger.debug("Creating Database")
    cursor = None
    try:
        await db_connect()

        if app_config.DB_CONN_OPEN:
            cursor = app_config.DB_CONN.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                username VARCHAR(20) NOT NULL UNIQUE,
                                first_name VARCHAR(20) NOT NULL,
                                last_name VARCHAR(20),
                                email VARCHAR(50) NOT NULL);''')
            logger.debug("users table created")
            app_config.DB_CONN.commit()
            return {"status": True, "message": "Database created"}
        else:
            logger.error("Connection not open, cannot create database.")
            return {"status": False, "message": "Connection not open"}
    except sqlite3.OperationalError as op_err:
        logger.error(f"Operational error while creating table - {op_err}")
        app_config.DB_CONN_OPEN = False
        await db_connect()
        raise HTTPException(status_code=500, detail={"status": False, "message": f"Operational error - {op_err}"})
    except Exception as err:
        logger.error(f"Error while creating table - {err}")
        return {"status": False, "message": f"Error - {err}"}
    finally:
        if cursor:
            cursor.close()
        if app_config.DB_CONN_OPEN:
            await db_disconnect()


async def create_user(first_name, email, last_name=""):
    logger.debug("Creating User")
    cursor = None
    try:
        await db_connect()

        if app_config.DB_CONN_OPEN:
            cursor = app_config.DB_CONN.cursor()
            cursor.execute('''INSERT INTO users (first_name, last_name, email) 
                              VALUES (?, ?, ?)''', (first_name, last_name, email))
            app_config.DB_CONN.commit()
        else:
            logger.error("Connection not open, cannot create user.")
    except sqlite3.OperationalError as op_err:
        logger.error(f"Operational error while creating user - {op_err}")
        app_config.DB_CONN_OPEN = False
        await db_connect()
    except Exception as err:
        logger.error(f"Error while creating user: {err}")
    finally:
        if cursor:
            cursor.close()
        if app_config.DB_CONN_OPEN:
            await db_disconnect()


async def check_table_exists(table_name):
    logger.debug(f"Checking if {table_name} exists")
    cursor = None
    try:
        await db_connect()

        if app_config.DB_CONN_OPEN:
            cursor = app_config.DB_CONN.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
            table_exists = cursor.fetchone() is not None
            if table_exists:
                logger.debug(f"{table_name} exists")
            else:
                logger.debug(f"{table_name} does not exist")
            return table_exists
        else:
            logger.error("Connection not open, cannot check table existence.")
            return False
    except sqlite3.Error as err:
        logger.error(f"Error while checking if table exists: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if app_config.DB_CONN_OPEN:
            await db_disconnect()
