#!/usr/bin/env python3

import sys
import os
import json
import cgi
import cgitb

cgitb.enable()  # Enable detailed error reporting in browser

# === CONFIGURATION: Allowed Origins ===
ALLOWED_ORIGINS = [
    "chrome-extension://opialijmchklldmkipeobdalapddbbca",
    "chrome-extension://dkjfmaelhonjgombiigplfeelicmgehm"
]

def send_cors_headers(origin):
    if origin in ALLOWED_ORIGINS:
        print(f"Access-Control-Allow-Origin: {origin}")
        print("Access-Control-Allow-Credentials: true")
    print("Access-Control-Allow-Methods: POST, GET, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")

def main():
    origin = os.environ.get("HTTP_ORIGIN", "")

    # Handle preflight OPTIONS request
    if os.environ.get("REQUEST_METHOD") == "OPTIONS":
        send_cors_headers(origin)
        print("Content-Type: text/plain")
        print("Content-Length: 0\n")
        return

    # Start normal response
    send_cors_headers(origin)
    print("Content-Type: application/json\n")

    # Read JSON from stdin
    try:
        content_length = int(os.environ.get("CONTENT_LENGTH", 0))
        raw_input = sys.stdin.read(content_length)
        data = json.loads(raw_input)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return

    # Extract "id" fields
    id_list = [item["id"] for item in data if "id" in item]

    # Output JSON response
    print(json.dumps({"list": id_list}))

if __name__ == "__main__":
    main()
