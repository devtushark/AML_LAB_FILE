# log_generator.py

import logging
import time
import random
import psutil
import json
from datetime import datetime
import os # Import os module

# --- Configuration ---
LOG_FILE = "/app_logs/app_logs.log" # <--- CORRECTED PATH
TELEMETRY_FILE = "/app_logs/telemetry_data.json" # <--- CORRECTED PATH
LOG_INTERVAL_SECONDS = 1 # How often to generate a log entry
TELEMETRY_INTERVAL_SECONDS = 5 # How often to collect telemetry
ERROR_RATE = 0.1 # Probability of generating an error log (10%)
ANOMALY_RATE = 0.05 # Probability of generating an "anomalous" log entry (2%)
MAX_LOG_SIZE_MB = 5 # Maximum size of log file before rotation (for simplicity)

# --- Setup Logging ---
# Ensure the directory exists before configuring logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_FILE,
    filemode='a' # Append to the file if it exists
)
logger = logging.getLogger(__name__)

# --- Sample Log Messages ---
NORMAL_LOG_MESSAGES = [
    "User 'john_doe' logged in successfully from IP 192.168.1.10",
    "Database connection established for service 'auth-service'.",
    "Processing request for order #12345. Status: SUCCESS.",
    "API endpoint /api/v1/data accessed by user 'admin'.",
    "Background task 'data_sync' completed in 1.25s.",
    "System health check passed.",
    "Cache refreshed for user session.",
    "New user registered: 'jane_smith'.",
    "Payment gateway responded with status 200.",
    "Data written to disk: /var/log/app.log",
]

ERROR_LOG_MESSAGES = [
    "ERROR: Failed to connect to database. Retrying in 5 seconds...",
    "CRITICAL: Disk usage is 98% on /dev/sda1. Immediate attention required!",
    "WARNING: High latency detected for API call to external_service (3500ms).",
    "ERROR: Invalid input received from user 'malicious_user' (SQL Injection attempt suspected).",
    "CRITICAL: Memory allocation failed. System might become unresponsive.",
    "ERROR: Authentication failed for user 'unknown_user'. Invalid credentials.",
    "WARNING: Too many open files. Adjusting ulimit.",
    "ERROR: Network timeout when reaching remote host 10.0.0.5.",
]

ANOMALOUS_LOG_MESSAGES = [
    "ALERT: Unusual number of login failures from a single IP address: 203.0.113.44. Possible brute-force attack.",
    "CRITICAL: Unauthorized access attempt detected on sensitive file /etc/shadow from user 'guest'.",
    "WARNING: Unexpected surge in read operations on database. QPS increased by 500% in 1 minute.",
    "ERROR: Core system process 'kernel_module' crashed unexpectedly. Reboot recommended.",
    "SECURITY: Multiple failed SSH attempts from different geographic locations. Account 'root' locked.",
    "ALERT: Large data transfer detected from internal server to external IP (unapproved).",
    "ANOMALY: Application restart count exceeded threshold (5 restarts in 10 minutes).",
    "URGENT: Abnormal CPU utilization spike (99%) for sustained 5 minutes on critical service.",
]

def generate_log_entry():
    """Generates a synthetic log entry, sometimes an error or anomaly."""
    # Simple log file rotation
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE_MB * 1024 * 1024:
        logger.info(f"Log file {LOG_FILE} reached max size, rotating.")
        # In a real system, you'd move/compress the file. Here, we just clear for simplicity.
        with open(LOG_FILE, 'w') as f:
            f.write("")

    if random.random() < ANOMALY_RATE:
        message = random.choice(ANOMALOUS_LOG_MESSAGES)
        logger.error(f"ANOMALY DETECTED: {message}")
    elif random.random() < ERROR_RATE:
        message = random.choice(ERROR_LOG_MESSAGES)
        logger.warning(message) # Use warning for errors
    else:
        message = random.choice(NORMAL_LOG_MESSAGES)
        logger.info(message)

def get_telemetry_data():
    """Collects system telemetry data using psutil."""
    telemetry = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=None), # Non-blocking call
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage('/').percent,
        "network_io_bytes_sent": psutil.net_io_counters().bytes_sent,
        "network_io_bytes_recv": psutil.net_io_counters().bytes_recv,
    }
    return telemetry

def write_telemetry_data(data):
    """Appends telemetry data to a JSON file."""
    try:
        with open(TELEMETRY_FILE, 'a') as f:
            f.write(json.dumps(data) + '\n')
    except Exception as e:
        logger.error(f"Failed to write telemetry data: {e}")

# Main loop to generate logs and telemetry
import threading

def log_generation_loop():
    while True:
        generate_log_entry()
        time.sleep(LOG_INTERVAL_SECONDS)

def telemetry_collection_loop():
    while True:
        telemetry = get_telemetry_data()
        write_telemetry_data(telemetry)
        time.sleep(TELEMETRY_INTERVAL_SECONDS)

if __name__ == "__main__":
    print(f"Generating logs to {LOG_FILE} and telemetry to {TELEMETRY_FILE}...")
    print("Press Ctrl+C to stop.")

    # Start log generation in a separate thread
    log_thread = threading.Thread(target=log_generation_loop)
    log_thread.daemon = True # Allow main program to exit even if this thread is running
    log_thread.start()

    # Start telemetry collection in a separate thread
    telemetry_thread = threading.Thread(target=telemetry_collection_loop)
    telemetry_thread.daemon = True
    telemetry_thread.start()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping log and telemetry generation.")
        # Threads are daemon, so they will exit when main thread exits
