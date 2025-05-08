#!/usr/bin/env python3

import sys
import json
import cgi
import cgitb

cgitb.enable()  # Enable detailed error reporting in browser

def main():

    # Handle preflight requests
    if os.environ['REQUEST_METHOD'] == 'OPTIONS':
        print("Access-Control-Allow-Origin: chrome-extension://opialijmchklldmkipeobdalapddbbca")
        print("Access-Control-Allow-Methods: POST, GET, OPTIONS")
        print("Access-Control-Allow-Headers: Content-Type")
        print("Access-Control-Allow-Credentials: true\n")
        sys.exit(0)
    
 
    
    # Read JSON from stdin
    try:
        content_length = int(os.environ.get("CONTENT_LENGTH", 0))
        raw_input = sys.stdin.read(content_length)
        data = json.loads(raw_input)
    except Exception as e:
        print("Content-Type: application/json\n")
        print(json.dumps({"error": str(e)}))
        return

    # Example: Assume data is { "items": [...] }
    if "items" in data and isinstance(data["items"], list):
        item_list = data["items"]
    else:
        item_list = []

    # Return list as JSON
    print("Content-Type: application/json")
    print("Access-Control-Allow-Methods: POST, GET, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print("Access-Control-Allow-Origin: chrome-extension://opialijmchklldmkipeobdalapddbbca\n")  # Allow extension to fetch this
    print(json.dumps({"list": item_list}))

if __name__ == "__main__":
    import os
    main()

