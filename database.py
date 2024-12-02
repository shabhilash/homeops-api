import sqlite3

from fastapi import HTTPException
from conf import app_config

# Logger
root_logger = app_config.logger
logger = root_logger.getChild('db')

conn = None  # Global connection variable
conn_open = False  # Global flag to track connection state


async def db_connect():
    global conn, conn_open
    if not conn_open:
        try:
            conn = sqlite3.connect(app_config.DB_NAME)
            conn_open = True
            logger.debug("Connected to database")
        except Exception as err:
            logger.error(f"Error connecting to database - {err}")
            conn_open = False


async def db_disconnect():
    global conn, conn_open
    if conn_open and conn:
        conn.close()
        conn_open = False
        logger.debug("Database connection closed.")


async def create_database():
    global conn, conn_open
    logger.debug("Creating Database")
    try:
        # Ensure the connection is open
        await db_connect()

        if conn_open:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username VARCHAR(20) NOT NULL UNIQUE,
                                first_name VARCHAR(20) NOT NULL,
                                last_name VARCHAR(20),
                                email VARCHAR(20) NOT NULL);''')
            logger.debug("users table created")
            conn.commit()
            cursor.close()
            return {"status": True, "message": "Database created"}
        else:
            logger.error("Connection not open, cannot create database.")
            return {"status": False, "message": "Connection not open"}
    except sqlite3.OperationalError as op_err:
        logger.error(f"Operational error while creating table - {op_err}")
        conn_open = False
        await db_connect()
        raise HTTPException(status_code=500, detail=f'{
                            "status": False, "message": f"Operational error - {op_err}"}')
    except Exception as err:
        logger.error(f"Error while creating table - {err}")
        return {"status": False, "message": f"Error - {err}"}
    finally:
        if conn_open:
            cursor.close()
        # Do not close the connection here if you're going to reuse it


async def create_user(first_name, email, last_name=""):
    global conn, conn_open
    logger.debug("Creating User")
    try:
        # Ensure the connection is open
        await db_connect()

        if conn_open:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users (first_name, last_name, email) 
                              VALUES (?, ?, ?)''', (first_name, last_name, email))
            conn.commit()
            cursor.close()
        else:
            logger.error("Connection not open, cannot create user.")
    except sqlite3.OperationalError as op_err:
        logger.error(f"Operational error while creating user - {op_err}")
        conn_open = False
        await db_connect()
    except Exception as err:
        logger.error(f"Error while creating user: {err}")


async def check_table_exists(table_name):
    '''
    Function to check if the table exists
    '''
    await db_connect()
    logger.debug(f"Checking if {table_name} exists")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name={table_name};")
    table_exists = cursor.fetchone() is not None
    if table_exists:
        logger.debug(f"{table_name} exists")
    else:
        logger.debug(f"{table_name} does not exists")
    conn.close()
    return table_exists
