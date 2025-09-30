import os
import logging
import requests
import ipaddress
from datetime import datetime, timedelta
import azure.functions as func

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from azure.mgmt.web import WebSiteManagementClient

# ----------------------------------------------------
# Load environment variables with debug logging
# ----------------------------------------------------
REQUIRED_ENV_VARS = [
    "WORKSPACE_ID",
    "SUBSCRIPTION_ID",
    "RESOURCE_GROUP",
    "APP_SERVICE_NAME",
    "ABUSEIPDB_API_KEY"
]

missing = [v for v in REQUIRED_ENV_VARS if v not in os.environ]
if missing:
    logging.error(f"❌ Missing required environment variables: {missing}")
    raise Exception(f"Missing required environment variables: {missing}")

WORKSPACE_ID = os.environ["WORKSPACE_ID"]
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["RESOURCE_GROUP"]
APP_SERVICE_NAME = os.environ["APP_SERVICE_NAME"]
ABUSEIPDB_API_KEY = os.environ["ABUSEIPDB_API_KEY"]

# ----------------------------------------------------
# Helper: Check if IP is listed in AbuseIPDB
# ----------------------------------------------------
def is_malicious_ip(ip):
    try:
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {
            "Key": ABUSEIPDB_API_KEY,
            "Accept": "application/json"
        }
        params = {"ipAddress": ip, "maxAgeInDays": 90}

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            reports = data.get("data", {}).get("totalReports", 0)
            return reports > 0
        else:
            logging.warning(f"⚠️ AbuseIPDB check failed for {ip}: {response.text}")
            return False
    except Exception as e:
        logging.error(f"❌ Error checking AbuseIPDB for {ip}: {e}")
        return False

# ----------------------------------------------------
# Azure Function entry point
# ----------------------------------------------------
def main(mytimer: func.TimerRequest) -> None:
    logging.info("🚀 Function blockMaliciousIps triggered")

    try:
        # Authenticate with Azure
        credential = DefaultAzureCredential()
        logs_client = LogsQueryClient(credential)
        web_client = WebSiteManagementClient(credential, SUBSCRIPTION_ID)

        # Query App Service logs for unique client IPs (last 24 hours)
        query = f"""
        AppServiceHTTPLogs
        | where TimeGenerated > ago(24h)
        | where isnotempty(CIp)
        | summarize by CIp
        """
        timespan = timedelta(hours=24)
        response = logs_client.query_workspace(WORKSPACE_ID, query, timespan=timespan)

        if not response.tables:
            logging.info("✅ No logs found in last 24h")
            return

        candidate_ips = [row[0] for row in response.tables[0].rows]
        logging.info(f"🔍 Found {len(candidate_ips)} unique IPs in logs")

        # Check AbuseIPDB for malicious IPs
        malicious_ips = []
        for ip in candidate_ips:
            if is_malicious_ip(ip):
                malicious_ips.append(ip)
                logging.info(f"🚫 Malicious IP detected: {ip}")

        if not malicious_ips:
            logging.info("✅ No malicious IPs detected. Nothing to block.")
            return

        # Fetch existing IP restrictions
        config = web_client.web_apps.get_configuration(RESOURCE_GROUP, APP_SERVICE_NAME)
        existing_rules = config.ip_security_restrictions or []

        # Add deny rules for malicious IPs
        for ip in malicious_ips:
            cidr = f"{ip}/32"
            if any(r.ip_address == cidr for r in existing_rules):
                logging.info(f"ℹ️ IP {ip} already blocked, skipping")
                continue

            rule = {
                "ip_address": cidr,
                "action": "Deny",
                "priority": 500,
                "name": f"Block_{ip.replace('.', '_')}"
            }
            existing_rules.append(rule)
            logging.info(f"🚫 Blocking IP: {ip}")

        # Update configuration
        config.ip_security_restrictions = existing_rules
        web_client.web_apps.update_configuration(
            RESOURCE_GROUP, APP_SERVICE_NAME, config
        )

        logging.info(f"✅ Blocked {len(malicious_ips)} malicious IP(s): {malicious_ips}")

    except Exception as e:
        logging.error(f"❌ Function failed: {e}")
