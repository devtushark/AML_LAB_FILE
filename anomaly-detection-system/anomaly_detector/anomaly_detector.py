# anomaly_detector.py

import os
import time
import json
import requests
import threading
from datetime import datetime

# --- Configuration ---
LOG_FILE = "/app_logs/app_logs.log" # <--- CORRECTED PATH FOR SHARED VOLUME
TELEMETRY_FILE = "/app_logs/telemetry_data.json" # <--- CORRECTED PATH FOR SHARED VOLUME
NOTIFICATION_SERVICE_URL = "http://notification_service:5001/notify_anomaly" # Changed for Docker Compose
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") # Get API key from environment variable
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
CHECK_INTERVAL_SECONDS = 2 # How often to check for new log/telemetry entries

# --- Global state for file pointers ---
log_file_pointer = 0
telemetry_file_pointer = 0

# --- Helper function to call Gemini AI API ---
async def call_gemini_api(prompt_text):
    """
    Calls the Gemini AI API with the given prompt and returns the text response.
    Note: This function is asynchronous and will be called using an event loop.
    """
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not set. Anomaly detection will not function.")
        return "API_KEY_MISSING"

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        ]
    }
    # Append API key directly to URL if not set in environment or handled by Canvas runtime
    api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}" if GEMINI_API_KEY else GEMINI_API_URL

    try:
        # Using requests for synchronous call. For production, consider aiohttp for async.
        response = requests.post(api_url_with_key, headers=headers, json=payload, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        result = response.json()

        if result.get('candidates') and len(result['candidates']) > 0 and \
           result['candidates'][0].get('content') and \
           result['candidates'][0]['content'].get('parts') and \
           len(result['candidates'][0]['content']['parts']) > 0:
            return result['candidates'][0]['content'].get('parts')[0].get('text', '') # Ensure text is retrieved correctly
        else:
            print(f"Gemini API response missing content: {result}")
            return "NO_CONTENT"
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return f"API_ERROR: {e}"
    except json.JSONDecodeError as e:
        print(f"Error decoding Gemini API response: {e}")
        return f"JSON_DECODE_ERROR: {e}"

# --- Function to send anomaly notification ---
def send_notification(anomaly_details):
    """Sends anomaly details to the notification service."""
    try:
        response = requests.post(NOTIFICATION_SERVICE_URL, json=anomaly_details, timeout=5)
        response.raise_for_status()
        print(f"Sent anomaly notification: {anomaly_details['message']}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification to {NOTIFICATION_SERVICE_URL}: {e}")

# --- Anomaly Detection Logic for Logs ---
async def check_log_anomaly(log_entry):
    """
    Analyzes a single log entry for anomalies using Gemini AI.
    """
    print(f"Analyzing log: {log_entry.strip()}")
    prompt = (
        f"Analyze the following log entry and determine if it indicates an anomaly, security threat, "
        f"or a critical system issue. Respond with 'ANOMALY' if it's anomalous/critical, "
        f"'NORMAL' otherwise. If ANOMALY, also provide a brief reason why.\n\nLog Entry: {log_entry.strip()}"
        f"\n\nExample ANOMALY response: ANOMALY: Possible brute-force attack due to multiple login failures."
        f"\nExample NORMAL response: NORMAL"
    )
    response_text = await call_gemini_api(prompt)

    if response_text.startswith("ANOMALY:"):
        anomaly_reason = response_text[len("ANOMALY:"):].strip()
        notification_message = f"Log Anomaly Detected: {log_entry.strip()}. Reason: {anomaly_reason}"
        anomaly_details = {
            "type": "log_anomaly",
            "timestamp": datetime.now().isoformat(),
            "message": notification_message,
            "original_log": log_entry.strip(),
            "reason": anomaly_reason
        }
        send_notification(anomaly_details)
    elif response_text == "NORMAL":
        print(f"Log entry is NORMAL: {log_entry.strip()}")
    else:
        print(f"Gemini response for log was unclear or error: {response_text}. Log: {log_entry.strip()}")

# --- Anomaly Detection Logic for Telemetry ---
# Simple thresholding combined with AI (for more complex scenarios)
async def check_telemetry_anomaly(telemetry_data):
    """
    Analyzes telemetry data for anomalies using a combination of thresholds and Gemini AI.
    For simplicity, we'll use basic thresholds here, but Gemini could analyze trends.
    """
    cpu_percent = telemetry_data.get("cpu_percent", 0)
    memory_percent = telemetry_data.get("memory_percent", 0)
    disk_usage_percent = telemetry_data.get("disk_usage_percent", 0)

    # Basic thresholding for immediate alerts
    if cpu_percent > 90:
        message = f"High CPU usage: {cpu_percent}%"
        anomaly_details = {
            "type": "telemetry_anomaly",
            "timestamp": telemetry_data.get("timestamp", datetime.now().isoformat()),
            "metric": "CPU",
            "value": cpu_percent,
            "threshold": ">90%",
            "message": message
        }
        send_notification(anomaly_details)
        print(f"Telemetry Anomaly (High CPU): {message}")
        return # Don't send to AI if already alerted by threshold

    if memory_percent > 85:
        message = f"High Memory usage: {memory_percent}%"
        anomaly_details = {
            "type": "telemetry_anomaly",
            "timestamp": telemetry_data.get("timestamp", datetime.now().isoformat()),
            "metric": "Memory",
            "value": memory_percent,
            "threshold": ">85%",
            "message": message
        }
        send_notification(anomaly_details)
        print(f"Telemetry Anomaly (High Memory): {message}")
        return

    if disk_usage_percent > 95:
        message = f"High Disk usage: {disk_usage_percent}%"
        anomaly_details = {
            "type": "telemetry_anomaly",
            "timestamp": telemetry_data.get("timestamp", datetime.now().isoformat()),
            "metric": "Disk",
            "value": disk_usage_percent,
            "threshold": ">95%",
            "message": message
        }
        send_notification(anomaly_details)
        print(f"Telemetry Anomaly (High Disk): {message}")
        return

    # For more subtle telemetry anomalies, we can involve Gemini AI
    # Example: Ask Gemini to detect unusual patterns if thresholds aren't breached but metrics are fluctuating oddly.
    # For now, let's keep it simple with explicit thresholding for speed.
    # A more advanced prompt might include recent historical data for context.
    # prompt = (
    #     f"Analyze the following system telemetry data point in the context of typical system behavior. "
    #     f"Is this data point anomalous? Respond with 'ANOMALY' or 'NORMAL' and a brief reason if anomalous.\n\n"
    #     f"Telemetry: {json.dumps(telemetry_data)}"
    # )
    # response_text = await call_gemini_api(prompt)
    # if response_text.startswith("ANOMALY:"):
    #     anomaly_reason = response_text[len("ANOMALY:"):].strip()
    #     notification_message = f"Telemetry Anomaly Detected: {json.dumps(telemetry_data)}. Reason: {anomaly_reason}"
    #     anomaly_details = {
    #         "type": "telemetry_anomaly",
    #         "timestamp": telemetry_data.get("timestamp", datetime.now().isoformat()),
    #         "message": notification_message,
    #         "original_data": telemetry_data,
    #         "reason": anomaly_reason
    #     }
    #     send_notification(anomaly_details)
    # else:
    #     print(f"Telemetry data is NORMAL: {telemetry_data}")


# --- File Tailing Functions ---
def tail_file(filepath, initial_position, process_func, is_json=False):
    """
    Continuously reads new lines from a file from a given initial position.
    `process_func` is an async function to be called for each new line.
    """
    global log_file_pointer, telemetry_file_pointer # Declare global to modify
    current_position = initial_position

    # Check if the file exists
    if not os.path.exists(filepath):
        # If the file doesn't exist yet, we'll wait for it to be created.
        print(f"Waiting for file {filepath} to be created...")
        return current_position # Return current_position without changing it

    try:
        with open(filepath, 'r') as f:
            # If the file was truncated (smaller than last known position), reset pointer
            if os.path.getsize(filepath) < current_position:
                current_position = 0
                print(f"File {filepath} was truncated. Resetting read pointer to 0.")

            f.seek(current_position)
            new_lines = f.readlines()

            if new_lines:
                for line in new_lines:
                    if line.strip(): # Process non-empty lines
                        if is_json:
                            try:
                                data = json.loads(line.strip())
                                # We need an event loop to run async functions
                                import asyncio
                                asyncio.run(process_func(data))
                            except json.JSONDecodeError as e:
                                print(f"Skipping malformed JSON in {filepath}: {line.strip()}. Error: {e}")
                        else:
                            import asyncio
                            asyncio.run(process_func(line))
                current_position = f.tell() # Update pointer to the new end of the file
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")

    return current_position

# --- Main Tailing Loops ---
def log_tailer_loop():
    global log_file_pointer
    while True:
        log_file_pointer = tail_file(LOG_FILE, log_file_pointer, check_log_anomaly, is_json=False)
        time.sleep(CHECK_INTERVAL_SECONDS)

def telemetry_tailer_loop():
    global telemetry_file_pointer
    while True:
        telemetry_file_pointer = tail_file(TELEMETRY_FILE, telemetry_file_pointer, check_telemetry_anomaly, is_json=True)
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    # Ensure a directory for logs exists if running locally for dev purposes
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True) # Ensure /app_logs exists
    os.makedirs(os.path.dirname(TELEMETRY_FILE), exist_ok=True) # Ensure /app_logs exists

    print("Starting Anomaly Detection Backend...")
    print(f"Listening for logs from {LOG_FILE} and telemetry from {TELEMETRY_FILE}")
    print(f"Sending anomaly notifications to {NOTIFICATION_SERVICE_URL}")
    print("Press Ctrl+C to stop.")

    # Start log tailing in a separate thread
    log_tail_thread = threading.Thread(target=log_tailer_loop)
    log_tail_thread.daemon = True
    log_tail_thread.start()

    # Start telemetry tailing in a separate thread
    telemetry_tail_thread = threading.Thread(target=telemetry_tailer_loop)
    telemetry_tail_thread.daemon = True
    telemetry_tail_thread.start()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Anomaly Detection Backend.")
