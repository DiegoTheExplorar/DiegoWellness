# Use official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies (cache layer when requirements.txt doesn't change)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-telegram-bot[job-queue]
# Copy the rest of the application code
COPY . .

# Set environment variables (these should be passed at runtime or build time)
ARG BOT_TOKEN
ARG GROQ_API_KEY
ENV BOT_TOKEN=${BOT_TOKEN}
ENV GROQ_API_KEY=${GROQ_API_KEY}

# Command to run the application (array form is more robust)
CMD python app.py
