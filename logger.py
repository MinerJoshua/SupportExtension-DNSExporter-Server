import logging
import os
from config import LOG_DIR

def get_job_logger(job_id):
    """
    Returns a logger instance that writes to a file for a specific job.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"{job_id}.log")

    logger = logging.getLogger(f"job_{job_id}")

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.propagate = False  # prevent double logging to stdout

    return logger

