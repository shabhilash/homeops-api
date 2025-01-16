import os

import bcrypt
from dotenv import load_dotenv

import logging
from ldap3 import ALL, SAFE_SYNC, Connection, Server

from app.exceptions.exceptions import CustomHTTPException
from app.utils.db_init import SessionLocal
from app.utils.db_schemas import User

# Logger setup
logger = logging.getLogger("homeops.ad")
load_dotenv()

def get_user_from_db(session, username):
    """
    Function to fetch user data from the DB using SQLAlchemy
    """
    try:
        user = session.query(User).filter(User.username == username).first()  # Returns None if no user is found
        return user
    except Exception as err:
        logger.exception(f"Error while fetching user {username} from the database: {err}")
        return None


async def fetch_ad_users():
    """
    Function to fetch user data from the AD
    """
    try:
        username = os.getenv('AD_USERNAME')
        password = os.getenv("AD_PASSWORD")
        server_address = os.getenv("AD_SERVER")
        search_base = os.getenv("AD_BASEDN")
        search_filter = '(objectClass=user)'  # Filter to search for user objects
        attributes = ['sAMAccountName', 'givenName', 'sn', 'mail', 'memberOf']  # Including 'memberOf' for group membership
        domain = os.getenv("AD_DOMAIN")

        logger.debug(f"Using username: {username}, server_address: {server_address}, search_basecn: {search_base}, domain: {domain}")

        # Connect to the server
        server = Server(server_address, get_info=ALL)
        connection = Connection(server, username, password, client_strategy=SAFE_SYNC, auto_bind=True)

        # Perform the search
        status, result, response, _ = connection.search(search_base, search_filter, attributes=attributes)
        logger.debug(f"Search status: {status}, result: {result}")
        logger.info(f"AD Response: {len(response)}")

        # Extract relevant information from the response
        users = []
        for entry in response:
            if 'raw_attributes' in entry:
                s_am_account_name = entry['raw_attributes'].get('sAMAccountName')
                if isinstance(s_am_account_name, list):
                    s_am_account_name = s_am_account_name[0].decode("utf-8")
                if s_am_account_name and not s_am_account_name.endswith('$'):
                    email = entry['raw_attributes'].get('mail') or f"{s_am_account_name}@{domain}"
                    user_info = {
                        'username': s_am_account_name,
                        'first_name': entry['raw_attributes'].get('givenName'),
                        'last_name': entry['raw_attributes'].get('sn'),
                        'email': email,
                        'groups': entry['raw_attributes'].get('memberOf', [])  # Groups the user belongs to
                    }
                    users.append(user_info)
        return users

    except Exception as err:
        logger.error(f"Error while fetching AD users: {err}")
        raise CustomHTTPException(status_code=500, detail=f"Error while fetching AD users: {err}",code="AD_SYNC_ERROR_002")


async def check_if_superuser(username: str, group_name: str) -> bool:
    """
    Check if the user is part of the specified AD group.
    """
    try:
        # Create a connection to the AD server
        server = Server(os.getenv("AD_SERVER"))
        conn = Connection(server, user=os.getenv("AD_USERNAME"), password=os.getenv("AD_PASSWORD"), auto_bind=True)

        # Search for the user in the AD groups
        search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"
        conn.search(search_base=os.getenv("AD_BASEDN"), search_filter=search_filter, attributes=["memberOf"])

        if conn.entries:
            user = conn.entries[0]
            groups = user.memberOf.value if user.memberOf else []  # Safely handle None case

            # Check if the user is a member of the specified superuser group
            if any(group_name in group for group in groups):
                return True  # User is part of the superuser group
        return False  # User is not part of the group

    except Exception as err:
        logger.exception(f"Error checking group membership for {username}: {err}")
        return False



async def sync_ad_users():
    """
    Async function to add AD users to the database using SQLAlchemy.
    """
    modified_user_count = 0
    new_user_count = 0
    # noinspection PyUnusedLocal
    total_users_fetched = 0
    try:
        logger.debug("Adding AD users to users table")

        # Open a session to interact with the database
        session = SessionLocal()

        logger.debug("Fetching users from AD")
        users = await fetch_ad_users()  # Fetch AD users asynchronously
        logger.debug(f"Users fetched: {users}")
        total_users_fetched = len(users)

        # Specify the AD group that grants superuser privileges
        superuser_group = os.getenv("AD_SUPERUSER_GROUP") or "Admins"

        for user in users:
            logger.debug(f"Processing user {user['username']}")

            # Ensure first_name and last_name are strings
            first_name = ""
            if isinstance(user['first_name'], list) and user['first_name']:
                first_name = user['first_name'][0].decode('utf-8') if isinstance(user['first_name'][0], bytes) else user['first_name'][0]
            elif isinstance(user['first_name'], str):
                first_name = user['first_name']
            else:
                logger.warning(f"Missing or empty first_name for user {user['username']}")

            last_name = ""
            if isinstance(user['last_name'], list) and user['last_name']:
                last_name = user['last_name'][0].decode('utf-8') if isinstance(user['last_name'][0], bytes) else user['last_name'][0]
            elif isinstance(user['last_name'], str):
                last_name = user['last_name']
            else:
                logger.warning(f"Missing or empty last_name for user {user['username']}")

            email = user['email'] if isinstance(user['email'], str) else f"{user['username']}@domain.com"  # fallback for email if not found

            # Fetch the current user data from the DB
            current_user = get_user_from_db(session, user['username'])

            # Check if the user is a superuser by checking group membership in AD
            is_superuser = await check_if_superuser(user['username'], superuser_group)

            # Hash the password before saving it
            password_hash = bcrypt.hashpw(user['username'].encode('utf-8'), bcrypt.gensalt())

            if current_user:
                # Compare the existing data with the new data
                if (first_name != current_user.first_name) or (last_name != current_user.last_name) or (email != current_user.email_address) or (is_superuser != current_user.is_superuser):
                    try:
                        # Update the user
                        current_user.first_name = first_name
                        current_user.last_name = last_name
                        current_user.email_address = email
                        current_user.is_superuser = is_superuser
                        current_user.enabled = True  # Set enabled to True (you can adjust based on AD group)
                        current_user.password = password_hash.decode('utf-8')  # Store the hashed password
                        session.commit()
                        logger.debug(f"User {user['username']} updated in the database.")
                        modified_user_count += 1
                    except Exception as err:
                        logger.error(f"Error while updating user {user['username']} - {err}")
                        session.rollback()
                        continue
                else:
                    logger.debug(f"No changes for user {user['username']}, skipping update.")
            else:
                # Insert the new user with hashed password
                try:
                    new_user = User(
                        username=user['username'],
                        first_name=first_name,
                        last_name=last_name,
                        email_address=email,
                        password=password_hash.decode('utf-8'),  # Store the hashed password
                        is_superuser=is_superuser,  # Set based on AD group membership
                        enabled=True  # Assuming enabled by default; you can customize this
                    )
                    session.add(new_user)
                    session.commit()
                    logger.debug(f"User {user['username']} added to the database.")
                    new_user_count += 1
                except Exception as err:
                    logger.exception(f"Error while inserting new user {user['username']} - {err}")
                    session.rollback()
                    continue

        logger.info(f"User data imported. Total Users: {total_users_fetched}, New Users: {new_user_count}, Modified Users: {modified_user_count}")
        session.close()

    except Exception as err:
        logger.exception(f"Error while syncing users: {err}")
        raise CustomHTTPException(status_code=500, detail=f"Error while syncing users - {err}",code="AD_SYNC_ERROR_001")

    return total_users_fetched, new_user_count, modified_user_count

