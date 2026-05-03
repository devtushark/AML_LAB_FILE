# notification_service.py

from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

# In-memory storage for anomalies.
# In a production system, you'd use a database (e.g., Firestore, PostgreSQL, Redis).
anomalies_store = []
MAX_ANOMALIES = 100 # Keep a reasonable number of recent anomalies

# --- API Endpoints ---
@app.route('/notify_anomaly', methods=['POST'])
def receive_anomaly():
    """
    Receives anomaly notifications from the anomaly detection service.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    anomaly_data = request.get_json()
    print(f"Received anomaly: {anomaly_data}")

    # Add timestamp if not present (should be added by detector, but good for robustness)
    if 'timestamp' not in anomaly_data:
        anomaly_data['timestamp'] = datetime.now().isoformat()

    anomalies_store.append(anomaly_data)

    # Keep the list size in check
    if len(anomalies_store) > MAX_ANOMALIES:
        anomalies_store.pop(0) # Remove the oldest anomaly

    return jsonify({"status": "success", "message": "Anomaly received"}), 200

@app.route('/get_anomalies', methods=['GET'])
def get_anomalies():
    """
    Returns the list of stored anomalies.
    """
    return jsonify(anomalies_store), 200

# --- Health check endpoint ---
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy"}), 200

# --- CORS Configuration for development ---
# This is crucial for the web UI to access this API from a different port/origin.
# In production, configure your web server (Nginx, Apache) to handle CORS properly.
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response

# --- Run the Flask app ---
if __name__ == '__main__':
    print("Starting Anomaly Notification Service on port 5001...")
    # This will run the Flask development server.
    # For production, use a WSGI server like Gunicorn or uWSGI.
    app.run(host='0.0.0.0', port=5001, debug=False) # debug=False for safer production use
