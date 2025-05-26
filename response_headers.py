import json
import os
from config import ALLOWED_ORIGINS

def send_cors_headers(origin):
    if origin in ALLOWED_ORIGINS:
        print(f"Access-Control-Allow-Origin: {origin}")
        print("Access-Control-Allow-Credentials: true")
    print("Access-Control-Allow-Methods: POST, GET, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type, X-Session-Token")

def send_response_headers(content_type="application/json", status=200, origin=None):
    if origin:
        send_cors_headers(origin)

    if status != 200:
        status_messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error"
        }
        reason = status_messages.get(status, "Error")
        print(f"Status: {status} {reason}")
    else:
        print("Status: 200 OK")

    print(f"Content-Type: {content_type}")
    print()  # Required blank line

def send_json_response(data, status=200, origin=None):
    send_response_headers("application/json", status=status, origin=origin)
    print(json.dumps(data))

def handle_preflight(origin):
    send_response_headers("text/plain", status=200, origin=origin)
    print("Content-Length: 0")

