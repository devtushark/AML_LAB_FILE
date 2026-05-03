# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY log_generator.py .

# Create the directory for logs and telemetry data
# This is crucial for the shared volume
RUN mkdir -p /app_logs

# Command to run the application
CMD ["python", "log_generator.py"]
