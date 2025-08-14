#!/usr/bin/env python3
import requests
import socket
from datetime import datetime, timedelta, timezone
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Elasticsearch connection details
ES_HOST = "https://192.168.1.13:9200"
ES_USER = "elastic"
ES_PASS = "elastic123"
INDEX_PATTERN = "logs-*"
LOGS_THRESHOLD = 1000  # Minimum number of logs to trigger an alert

# Syslog server details
SYSLOG_SERVER = "192.168.1.12"
SYSLOG_PORT = 514

# Time range (last 5 minutes)
now = datetime.now(timezone.utc)
start_time = now - timedelta(minutes=5)

query = {
    "query": {
        "range": {
            "@timestamp": {
                "gte": start_time.isoformat(timespec='milliseconds').replace("+00:00", "Z"),
                "lte": now.isoformat(timespec='milliseconds').replace("+00:00", "Z")
            }
        }
    }
}

try:
    # Query Elasticsearch _count API
    url = f"{ES_HOST}/{INDEX_PATTERN}/_count"
    response = requests.get(
        url,
        auth=(ES_USER, ES_PASS),
        json=query,
        verify=False,
        timeout=10
    )

    if response.status_code != 200:
        print(f"[ERROR] Elasticsearch query failed: {response.status_code}, {response.text}")
        exit(1)

    data = response.json()
    doc_count = data.get("count", 0)
    print(f"[INFO] Found {doc_count} logs in the last 5 minutes.")

    if doc_count < LOGS_THRESHOLD:
        alert_msg = f"ALERT: Low log volume detected. Only {doc_count} logs in the last 5 mins."
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(alert_msg.encode(), (SYSLOG_SERVER, SYSLOG_PORT))
        print(f"[INFO] Alert sent to syslog server {SYSLOG_SERVER}:{SYSLOG_PORT}")
    else:
        print("[INFO] Log volume is normal. No alert sent.")

except Exception as e:
    print(f"[ERROR] {str(e)}")
