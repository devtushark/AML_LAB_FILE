# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY notification_service.py .

# Expose the port the Flask app runs on
EXPOSE 5001

# Command to run the application
CMD ["python", "notification_service.py"]
