import os
from db import (
    update_failed_job_item,
    cancel_job
)
from api_runner import fetch_package_dns
from zonefile_writer import convert_and_write_zone
from logger import get_job_logger

def process_job_items_streaming(job_id, package_ids, session_token):
    logger = get_job_logger(job_id)
    zone_paths = []
    
    consecutive_failures = 0
    max_consecutive_failures = 20
    failure_log_path = f"tmp/{job_id}_recent_failures.log"

    with open(failure_log_path, "w") as fail_log:
        for pkg_id in package_ids:
            logger.info(f"Processing package {pkg_id}")
            try:
                data = fetch_package_dns(pkg_id, session_token)
                if not data:
                    logger.info(f"Package {pkg_id} skipped due to Empty API result")
                    continue
                
                path = convert_and_write_zone(pkg_id, data, job_id)
                zone_paths.append(path)
                
                logger.info(f"Package {pkg_id} completed and written to {path}")
                consecutive_failures = 0

            except Exception as e:
                error_type = "api" if "fetch" in str(e).lower() else "conversion"
                logger.error(f"Package {pkg_id} failed ({error_type}): {e}")
                update_failed_job_item(job_id, pkg_id,error=str(e))

                fail_log.write(f"{pkg_id}: {error_type} error: {e}\n")
                consecutive_failures += 1
                raise
                
                if consecutive_failures >= max_consecutive_failures:
                    cancel_job(job_id, "20 consecutive failures")
                    logger.error("Cancelled job after 20 consecutive failures")
                    fail_log.write("Job cancelled after 20 consecutive failures\n")
                    return zone_paths,False

    return zone_paths,True

