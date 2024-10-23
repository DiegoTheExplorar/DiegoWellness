# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install python-telegram-bot[job-queue]

# Copy the rest of the application code into the container
COPY . .

# Run the application when the container starts
CMD python app.py
