import requests
import logging
import os

from config import SESSION_COOKIE_NAME


def fetch_package_dns(package_id, session_token):
    """
    Fetch DNS records for a specific package ID using session token.

    Args:
        package_id (int): The package ID
        session_token (str): PHP session ID from the client

    Returns:
        dict or None: Parsed JSON response from API, or None on failure
    """
    url = f"https://my.20i.com/a/package/{package_id}/dns"
    headers = {
        "Cookie": f"PHPSESSID={session_token}"
    }

    # Define the log directory and file name
    log_path = os.path.join("log","api.log")
    
    # Configure logging
    logging.basicConfig(
        filename=log_path,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.ok:
            return response.json()
        else:
            logging.info(f"API call failed for package {package_id}: {response.status_code}")
            return None
    except Exception as e:
        logging.info(f"Exception for package {package_id}: {e}")
        return None


def fetch_all_package_data(package_ids, session_token):
    """
    Fetch DNS data for a list of package IDs.

    Args:
        package_ids (list[int]): List of package IDs
        session_token (str): PHP session ID

    Returns:
        dict: { package_id: response_data or None }
    """
    results = {}
    for pkg_id in package_ids:
        results[pkg_id] = fetch_package_dns(pkg_id, session_token)
    return results

