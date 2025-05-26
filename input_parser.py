def flatten_packages(payload):
    """
    Extracts package IDs from validated payload.

    Args:
        payload (list): List of dicts like { "id": ..., "names": [...] }

    Returns:
        list[int]: List of package IDs
    """
    return [item["id"] for item in payload if "id" in item]

