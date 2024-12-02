from conf import app_config
from ldap3 import ALL, SAFE_SYNC, Connection, Server
import sqlite3
import logging
from fastapi import HTTPException

from database import db_connect

logger = logging.getLogger("autolab.db.ad")


def get_user_from_db(username):
    '''
    Function to fetch user data from the DB
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT username, first_name, last_name, email FROM users WHERE username = ?''', (username,))
        user_data = cursor.fetchone()  # Returns None if no user is found
        cursor.close()
        return user_data
    except sqlite3.Error as err:
        logger.error(f"Error while fetching user {
                     username} from the database: {err}")
        return None


async def fetch_ad_users():
    '''
    Function to fetch user data from the AD
    '''
    # Configuration
    username = app_config.config["AD"]["username"]
    password = app_config.config["AD"]["password"]
    server_address = app_config.config["AD"]["server"]
    search_base = 'dc=ashr,dc=duckdns,dc=org'
    search_filter = '(objectClass=user)'  # Filter to search for user objects
    attributes = ['sAMAccountName', 'givenName',
                  'sn', 'mail']  # Attributes to retrieve
    domain = app_config.config["AD"]["domain"]

    # Connect to the server
    server = Server(server_address, get_info=ALL)
    conn = Connection(server, username, password,
                      client_strategy=SAFE_SYNC, auto_bind=True)

    # Perform the search
    status, result, response, _ = conn.search(
        search_base, search_filter, attributes=attributes)

    # Extract relevant information from the response
    users = []
    for entry in response:
        if 'attributes' in entry:
            sAMAccountName = entry['attributes'].get('sAMAccountName')
            if sAMAccountName and not sAMAccountName.endswith('$'):
                email = entry['attributes'].get(
                    'mail') or f"{sAMAccountName}@{domain}"
                user_info = {
                    'username': sAMAccountName,
                    'first_name': entry['attributes'].get('givenName'),
                    'last_name': entry['attributes'].get('sn'),
                    'email': email
                }
                users.append(user_info)

    return users


async def add_ad_users():
    '''
    Async function to add AD users to the database
    '''
    global conn, conn_open
    logger.debug("Adding AD users to users table")

    try:
        await db_connect()

        if conn_open:
            cursor = conn.cursor()
            users = await fetch_ad_users()  # Fetch AD users asynchronously
            for user in users:
                logger.debug(f"Adding user {user['username']}")
                logger.debug(user)

                # Ensure first_name and last_name are strings
                first_name = user['first_name'] if isinstance(
                    user['first_name'], str) else ""
                last_name = user['last_name'] if isinstance(
                    user['last_name'], str) else ""
                email = user['email'] if isinstance(user['email'], str) else f"{
                    user['username']}@ashr.duckdns.org"

                # Fetch the current user data from the DB
                current_user = get_user_from_db(user['username'])

                # Only insert the user if any fields are modified
                if current_user:
                    db_first_name, db_last_name, db_email = current_user[
                        1], current_user[2], current_user[3]

                    # Compare the existing data with the new data
                    if (first_name != db_first_name) or (last_name != db_last_name) or (email != db_email):
                        try:
                            cursor.execute('''
                                INSERT OR REPLACE INTO users (username, first_name, last_name, email)
                                VALUES (?, ?, ?, ?)
                            ''', (user['username'], first_name, last_name, email))
                            conn.commit()
                            logger.debug(
                                f"User {user['username']} updated in the database.")
                        except sqlite3.Error as err:
                            logger.error(f"Error while inserting user {
                                         user['username']} - {err}")
                            continue  # Skip to the next user on error
                    else:
                        logger.debug(f"No changes for user {
                                     user['username']}, skipping update.")
                else:
                    # If the user does not exist in the DB, insert the new user
                    try:
                        cursor.execute('''
                            INSERT INTO users (username, first_name, last_name, email)
                            VALUES (?, ?, ?, ?)
                        ''', (user['username'], first_name, last_name, email))
                        conn.commit()
                        logger.debug(
                            f"User {user['username']} added to the database.")
                    except sqlite3.Error as err:
                        logger.error(f"Error while inserting new user {
                                     user['username']} - {err}")
                        continue  # Skip to the next user on error

            cursor.close()
        else:
            logger.error("Connection not open, cannot refresh users.")

    except sqlite3.DataError as err:
        logger.error(f"Error while processing data: {err}")
    except sqlite3.OperationalError as op_err:
        logger.error(f"Operational error while refreshing users - {op_err}")
        conn_open = False
        await db_connect()  # Try to reconnect
        raise HTTPException(
            status_code=500, detail=f"Operational error while refreshing users - {op_err}"
        )
    except sqlite3.Error as err:
        logger.error(f"Error while inserting data - {err}")
        raise HTTPException(
            status_code=500, detail=f"Error while inserting users - {err}"
        )
    except Exception as err:
        logger.error(f"Error while refreshing users: {err}")
        raise HTTPException(
            status_code=500, detail=f"Error while refreshing users - {err}"
        )
