# Use a lightweight official Python image
FROM python:3.14-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run Python's built-in simple HTTP server
#CMD ["python", "-m", "http.server", "8000"]
CMD ["python", "server.py"]

