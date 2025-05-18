#!/usr/bin/env python3

import sys
import os
import json
import gzip
import tempfile
import base64
import urllib.parse
from pathlib import Path
from io import BytesIO

# Send headers (include CORS headers!)
print("Content-Type: application/json")
print("Access-Control-Allow-Origin: *")
print("Access-Control-Allow-Methods: POST, OPTIONS")
print("Access-Control-Allow-Headers: Content-Type")
print()

# Handle preflight
if os.environ.get("REQUEST_METHOD") == "OPTIONS":
    print(json.dumps({"status": "ok"}))
    sys.exit(0)

def fqdn(name):
    return name if name.endswith('.') else name + '.'

def format_soa(record):
    return (
        f"{fqdn(record['host'])} IN SOA {fqdn(record['mname'])} {fqdn(record['rname'])} (\n"
        f"    {record['serial']} ; Serial\n"
        f"    {record['refresh']} ; Refresh\n"
        f"    {record['retry']}   ; Retry\n"
        f"    {record['expire']} ; Expire\n"
        f"    {record['minimum-ttl']} ) ; Minimum TTL\n"
    )

def format_record(record):
    host = fqdn(record["host"])
    rtype = record["type"]

    if rtype == "A":
        return f"{host} IN A {record['ip']}"
    elif rtype == "AAAA":
        return f"{host} IN AAAA {record['ipv6']}"
    elif rtype == "CNAME":
        return f"{host} IN CNAME {fqdn(record['target'])}"
    elif rtype == "NS":
        return f"{host} IN NS {fqdn(record['target'])}"
    elif rtype == "MX":
        return f"{host} IN MX {record['pri']} {fqdn(record['target'])}"
    elif rtype == "TXT":
        return f'{host} IN TXT "{record["txt"]}"'
    elif rtype == "SRV":
        return f"{fqdn(record['host'])} IN SRV {record['pri']} {record['weight']} {record['port']} {fqdn(record['target'])}"
    else:
        return f"; Unsupported record type: {rtype} for {host}"

def build_zone_file(domain, records):
    soa = next((r for r in records if r["type"] == "SOA"), None)
    others = [r for r in records if r["type"] != "SOA"]

    if not soa:
        return f"; No SOA record found for {domain}, skipping."

    lines = [f"$ORIGIN {fqdn(domain)}", f"$TTL {soa['minimum-ttl']}", "", format_soa(soa), ""]
    for rec in others:
        lines.append(format_record(rec))
    return "\n".join(lines)

def main():
    try:
        content_length = int(os.environ.get("CONTENT_LENGTH", 0))
        if content_length == 0:
            print("Error: Empty POST body.")
            return

        raw = sys.stdin.read(content_length)
        form = urllib.parse.parse_qs(raw)

        if "data" not in form:
            print("Error: 'data' field missing.")
            return

        b64_data = form["data"][0]
        compressed_bytes = base64.b64decode(b64_data)
        json_data = gzip.decompress(compressed_bytes).decode("utf-8")
        dns_data = json.loads(json_data)

        zone_dir = os.path.expanduser("~/dns_export/zonefiles")
        os.makedirs(zone_dir, exist_ok=True)
        temp_dir = tempfile.mkdtemp(prefix="zones_", dir=zone_dir)
        output_info = []

        for domain, records in dns_data.items():
            zone_text = build_zone_file(domain, records)
            file_path = Path(temp_dir) / f"{domain}.zone"
            with open(file_path, "w") as f:
                f.write(zone_text)
            output_info.append((domain, str(file_path)))

        print(json.dumps({
        "success": True,
            "files": [
            {"domain": domain, "path": path}
                for domain, path in output_info
            ]
        }))
        sys.stdout.flush()

    except Exception as e:
        print("Status: 500 Internal Server Error\n")
        print(f"Error: {str(e)}\n")
        print(traceback.format_exc())
        sys.stdout.flush()

if __name__ == "__main__":
    main()

