#!/usr/bin/env python3
import os
import sys
import json
import cgitb
import tempfile
import subprocess
from db import init_db
from http.cookies import SimpleCookie
from job_manager import start_job
from response_headers import send_json_response, handle_preflight

cgitb.enable()

def read_json_body():
    content_length = int(os.environ.get("CONTENT_LENGTH", 0))
    body = sys.stdin.read(content_length)
    return json.loads(body) if body else {}

def main():
    origin = os.environ.get("HTTP_ORIGIN", "")

    # Handle CORS preflight
    if os.environ.get("REQUEST_METHOD") == "OPTIONS":
        handle_preflight(origin)
        sys.exit(0)

    # Get session token from header or cookie
    session_token = os.environ.get("HTTP_X_SESSION_TOKEN")
    if not session_token:
        raw_cookie = os.environ.get("HTTP_COOKIE", "")
        cookies = SimpleCookie()
        cookies.load(raw_cookie)
        session = cookies.get("PHPSESSID")
        session_token = session.value if session else None

    if not session_token:
        send_json_response({ "error": "Missing session token" }, status=401, origin=origin)
        return

    # Parse request body
    payload = read_json_body()

    init_db()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as f:
        json.dump(payload, f)
    temp_path = f.name

    subprocess.Popen(["python3", "start_job_wrapper.py", temp_path, session_token])

    # Respond for now (will later call job_manager)
    send_json_response({
        "status": "ok",
        "received_token": session_token,
        "received_payload": payload
    }, origin=origin)


if __name__ == "__main__":
    main()

