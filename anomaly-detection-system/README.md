# Gemini-Powered Anomaly Detection System

This project demonstrates a real-time anomaly detection system built with Python, Flask, Nginx, and Docker Compose, leveraging the **Google Gemini AI** for intelligent log analysis. It simulates log and telemetry data generation, detects anomalies using AI and rule-based methods, and displays them on a simple web dashboard.

## 🚀 Features

* **Log & Telemetry Generation**: Simulates a live application generating various log messages (info, warning, error, critical) and system telemetry data (CPU, memory, disk, network).

* **AI-Powered Log Anomaly Detection**: Uses the **Gemini AI API** to analyze log entries for unusual patterns, security threats, or critical system issues.

* **Threshold-Based Telemetry Anomaly Detection**: Monitors system metrics (CPU, memory, disk) against predefined thresholds to flag abnormal resource usage.

* **Centralized Notification Service**: A lightweight Flask API to receive and store anomaly alerts.

* **Real-time Web Dashboard**: A simple HTML/JavaScript frontend to display incoming anomaly notifications dynamically.

* **Dockerized Deployment**: All components are containerized and orchestrated using Docker Compose for easy setup, isolation, and scalability.

* **Shared Volume for Data**: Logs and telemetry data are persisted and shared between generator and detector services using a Docker named volume.

## 🏗️ Architecture & Components

The system is composed of four main Dockerized services, communicating within a Docker network:

1. ### `log_generator` (Python)

   * **Purpose**: Simulates an application generating logs and telemetry data.

   * **Output**: Writes `app_logs.log` (plain text) and `telemetry_data.json` (JSON lines) into a shared Docker volume (`/app_logs`).

   * **Tech**: Python, `psutil` (for simulated system metrics).

2. ### `anomaly_detector` (Python)

   * **Purpose**: Reads logs and telemetry from the shared volume, analyzes them, and sends anomaly notifications.

   * **Log Analysis**: Connects to the **Gemini** AI **API** to classify log entries as 'ANOMALY' or 'NORMAL' based on a prompt.

   * **Telemetry Analysis**: Uses simple thresholding rules to detect high CPU, memory, or disk usage.

   * **Output**: Sends `POST` requests with anomaly details to the `notification_service`.

   * **Tech**: Python, `requests` (for API calls to Gemini and Notification Service).

3. ### `notification_service` (Python Flask API)

   * **Purpose**: Acts as a central API endpoint to receive and temporarily store anomaly alerts.

   * **Endpoints**:

     * `POST /notify_anomaly`: Receives anomaly details from `anomaly_detector`.

     * `GET /get_anomalies`: Provides the list of stored anomalies to the `web_ui`.

   * **Storage**: In-memory list (for demonstration purposes; replace with a database like Firestore, Redis, or PostgreSQL in production).

   * **Tech**: Python, Flask.

4. ### `web_ui` (HTML/JavaScript with Nginx)

   * **Purpose**: A simple web dashboard to visualize anomaly notifications in real-time.

   * **Data Fetching**: Periodically polls the `notification_service`'s `/get_anomalies` endpoint.

   * **Styling**: Uses Tailwind CSS via CDN.

   * **Tech**: HTML, JavaScript, Nginx (as a static file server).

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

* [**Docker Desktop**](https://www.docker.com/products/docker-desktop/): Includes Docker Engine and Docker Compose.

* [**Google Gemini API Key**](https://aistudio.google.com/app/apikey): You'll need to generate a key from Google AI Studio.

## 🚀 Getting Started

Follow these steps to get the anomaly detection system up and running on your local machine.

### 1. Project Structure

Create the following directory structure:

```
anomaly-detection-system/
├── app_logs/             # This directory will be created by Docker for shared logs
├── log_generator/
│   ├── log_generator.py
│   └── requirements.txt
│   └── Dockerfile        # Dockerfile for log_generator
├── anomaly_detector/
│   ├── anomaly_detector.py
│   └── requirements.txt
│   └── Dockerfile        # Dockerfile for anomaly_detector
├── notification_service/
│   ├── notification_service.py
│   └── requirements.txt
│   └── Dockerfile        # Dockerfile for notification_service
└── web_ui/
├── index.html
└── nginx.conf
└── Dockerfile        # Dockerfile for web_ui
└── docker-compose.yaml
```

### 3. Build and Run the System

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/mehuljn/anomaly-detection-system.git](https://github.com/mehuljn/anomaly-detection-system.git)
    cd anomaly-detection-system # Navigate into the cloned directory
    ```

2.  **Set Your Gemini API Key:**
    The `anomaly detector` require your `GEMINI_API_KEY`. It's recommended to set it as an environment variable in your shell.

    ```bash
    export GEMINI_API_KEY="YOUR_ACTUAL_GOOGLE_GEMINI_API_KEY_HERE"
    ```
    *Replace `"YOUR_ACTUAL_GOOGLE_GEMINI_API_KEY_HERE"` with your real API key in  `docker-compose.yml` as well.

3.  **Build and Run the Services:**
    From the root directory of the repository (`rag_cdc_pipeline/`), execute the following command:

    ```bash
    docker compose up --build -d
    ```


## 🌍 Accessing the Web Dashboard

Once all services are up and running, open your web browser and navigate to:

```
http://localhost:8080
```

You should see the "Anomaly Dashboard" and, after a short delay, start seeing generated log and telemetry entries being processed. Anomalies detected by Gemini AI or by threshold breaches will appear on the dashboard.

## 🧪 Triggering Anomalies (for Testing)

You can intentionally trigger anomalies by modifying the `log_generator.py` script.

1. **Stop the `log_generator` service**:


docker compose stop log_generator


2. **Edit `log_generator/log_generator.py`**:

* **For Log Anomalies**:

  * Change `ANOMALY_RATE = 0.02` to `ANOMALY_RATE = 1.0` (for 100% anomaly generation).

  * Or, temporarily insert a specific anomalous message directly into `generate_log_entry()` for a single-shot test.

* **For Telemetry Anomalies**:

  * Temporarily modify the `get_telemetry_data()` function to return artificially high values for `cpu_percent`, `memory_percent`, or `disk_usage_percent` (e.g., `cpu_percent: 98.0`).

**Remember to revert these changes after testing!**

3. **Restart the `log_generator` service**:


docker compose start log_generator


Monitor the dashboard and `anomaly_detector` logs (`docker compose logs -f anomaly_detector`) to see the triggered anomalies.

## 🛑 Stopping the Application

To stop all running services and remove their containers:

```bash
docker compose down
```

If you want to remove all associated volumes and images (for a very clean slate, useful for debugging persistent issues):

```bash
docker compose down --volumes --rmi all
```

## 📈 Future Enhancements

* **Persistent Anomaly Storage**: Integrate a real database (e.g., PostgreSQL, MongoDB, Redis, or a cloud service like Google Cloud Firestore) with the `notification_service` to persist anomalies beyond container restarts.

* **Real-time Notifications**: Implement WebSockets (e.g., Flask-SocketIO) for the `notification_service` and `web_ui` to push anomalies in real-time instead of polling.

* **Advanced Telemetry Analysis**: Use Gemini AI to detect more complex, multivariate anomalies or trends in telemetry data (e.g., using historical data as context in the prompt).

* **Alerting Mechanisms**: Add integrations for sending alerts to Slack, email, PagerDuty, etc.

* **User Authentication & Authorization**: Secure the `notification_service` and `web_ui`.

* **Data Visualization**: Enhance the web UI with graphs and charts for telemetry data and anomaly trends.

* **Configurability**: Externalize thresholds, rates, and other parameters into a configuration file.

