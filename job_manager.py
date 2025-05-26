# job_manager.py
import uuid
import json
from db import save_job, update_job_status
from input_parser import flatten_packages
from job_processor import process_job_items_streaming

def start_job(payload, session_token):
    job_id = str(uuid.uuid4())
    try:
        # Step 1: Save job record
        save_job(job_id, payload, status="starting")

        # Step 2: Convert to ID list
        update_job_status(job_id, "parsing package list")
        package_ids = flatten_packages(payload)

        # Step 3: API calls
        update_job_status(job_id, "fetching DNS data and writing to Zone file")
        writing_complete = process_job_items_streaming(job_id,package_ids,session_token)

        if writing_complete is not True:
            raise
    
        # Done
        update_job_status(job_id, "complete", result_path=";".join(zone_paths))
        return job_id, zone_paths

    except Exception as e:
        update_job_status(job_id, "failed", error=str(e))
        raise

