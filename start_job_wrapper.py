#!/usr/bin/env python3
import sys
import json
import os
import traceback
from datetime import datetime
from job_manager import start_job

def log(message):
    with open("tmp/job_runner.log", "a") as f:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        f.write(f"{timestamp} {message}\n")

def main():
    try:
        json_path = sys.argv[1]
        session_token = sys.argv[2]

        log(f"Starting job from {json_path} with session token: {session_token}")

        with open(json_path) as f:
            payload = json.load(f)

        os.remove(json_path)
        log(f"Deleted temp file {json_path}")

        start_job(payload, session_token)
        log("Job run successfully")

    except Exception as e:
        log(f"Exception occurred: {str(e)}")
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
