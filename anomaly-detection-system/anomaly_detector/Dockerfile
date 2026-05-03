# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY anomaly_detector.py .

# Command to run the application. GEMINI_API_KEY will be passed via docker-compose.yaml
CMD ["python", "anomaly_detector.py"]
