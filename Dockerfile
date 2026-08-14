# Use a lightweight official Python image
FROM python:3.14-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies if required by Spine/Flask
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Flask and Spine (with all optional visualization/core tools)
RUN pip install --no-cache-dir flask spine[all]

# Copy the current directory contents into the container
COPY . /app

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run Python's built-in simple HTTP server
#CMD ["python", "-m", "http.server", "8000"]
CMD ["python", "soap-server2.py"]

