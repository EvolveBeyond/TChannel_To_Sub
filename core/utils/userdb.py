import json
import os
import logging

# Get the absolute path of the directory where this script is located
# Then go up two levels to reach the project root
# Then join with 'data' and 'users.json'
# This makes the path resolution independent of where the script is run from,
# as long as the core/utils structure relative to project root is maintained.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'users.json')

# Ensure the data directory exists
DATA_DIR = os.path.dirname(DB_PATH)
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
        logging.info(f"Created data directory: {DATA_DIR}")
    except OSError as e:
        logging.error(f"Error creating data directory {DATA_DIR}: {e}")
        # Depending on desired behavior, might raise the error or exit
        raise

# Initialize the JSON file if it doesn't exist or is empty
if not os.path.isfile(DB_PATH) or os.path.getsize(DB_PATH) == 0:
    try:
        with open(DB_PATH, 'w') as f:
            json.dump({}, f)
        logging.info(f"Initialized user database: {DB_PATH}")
    except IOError as e:
        logging.error(f"Error initializing user database {DB_PATH}: {e}")
        raise

def get_user(uid: int) -> dict:
    """
    Retrieves user data from the JSON file.
    Returns an empty dict if user not found or if there's a file error.
    """
    try:
        with open(DB_PATH, 'r') as f:
            # Ensure file is not empty before trying to load
            if os.path.getsize(DB_PATH) == 0:
                return {} # Empty file means no data
            data = json.load(f)
        return data.get(str(uid), {})
    except FileNotFoundError:
        # If file doesn't exist, it means no users are stored yet.
        logging.info(f"{DB_PATH} not found in get_user. Returning empty data for user {uid}.")
        return {}
    except json.JSONDecodeError as e:
        logging.warning(f"JSONDecodeError in get_user for {DB_PATH}: {e}. Returning empty data for user {uid}.")
        return {}
    except IOError as e:
        logging.error(f"IOError in get_user for {DB_PATH}: {e}")
        return {}

def set_user(uid: int, **kwargs):
    """
    Sets or updates user data in the JSON file.
    """
    uid_str = str(uid)
    data = {}
    try:
        # Try to read existing data only if file exists and is not empty
        if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
            with open(DB_PATH, 'r') as f:
                data = json.load(f)
    except FileNotFoundError:
        # File not found, will create it. This is fine.
        logging.info(f"{DB_PATH} not found in set_user. Will create a new file.")
        data = {}
    except json.JSONDecodeError as e:
        # If file is corrupted, log warning and start with an empty dataset.
        # This means corrupted data will be overwritten.
        logging.warning(f"JSONDecodeError reading {DB_PATH} in set_user: {e}. Starting with fresh data structure.")
        data = {}
    except IOError as e:
        logging.error(f"IOError reading {DB_PATH} in set_user: {e}. Cannot proceed with update for user {uid_str}.")
        return # Or raise an error to indicate failure

    user_data = data.get(uid_str, {})
    user_data.update(kwargs)
    data[uid_str] = user_data

    try:
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logging.error(f"Could not write to {DB_PATH} in set_user for user {uid_str}: {e}")
        # Or raise an error

def get_all_users_data() -> dict:
    """
    Retrieves all user data from the JSON file.
    Returns an empty dict if there's a file error or file is empty.
    """
    try:
        with open(DB_PATH, 'r') as f:
            if os.path.getsize(DB_PATH) == 0: # Check if file is empty
                return {}
            data = json.load(f)
        return data
    except FileNotFoundError:
        logging.info(f"{DB_PATH} not found in get_all_users_data. Returning empty data.")
        return {}
    except json.JSONDecodeError as e:
        logging.warning(f"JSONDecodeError in get_all_users_data for {DB_PATH}: {e}. Returning empty data.")
        return {}
    except IOError as e:
        logging.error(f"IOError in get_all_users_data for {DB_PATH}: {e}")
        return {}
