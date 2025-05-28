import os
from pathlib import Path

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

    lines = [
        f"$ORIGIN {fqdn(domain)}",
        f"$TTL {soa['minimum-ttl']}",
        "",
        format_soa(soa),
        ""
    ]
    for rec in others:
        lines.append(format_record(rec))
    return "\n".join(lines)

def convert_and_write_zone(package_id, api_data, job_id, output_dir="zone_jobs"):
    """
    Converts DNS JSON to a .zone file.

    Args:
        package_id (int): ID of the package
        api_data (dict): DNS data (must contain domain as key and record list)
        job_id (str): Job UUID
        output_dir (str): Base output path for all zone files

    Returns:
        str: Path to the written zone file
    """
    os.makedirs(output_dir, exist_ok=True)
    job_path = os.path.join(output_dir, job_id)
    os.makedirs(job_path, exist_ok=True)

    written_files = []

    for domain, data in api_data.items():
        records = data.get("records", [])
        zone_text = build_zone_file(domain, records)
        file_path = Path(job_path) / f"{domain}.zone"
        with open(file_path, "w") as f:
            f.write(zone_text)
        written_files.append(str(file_path))

    return written_files[0] if written_files else None