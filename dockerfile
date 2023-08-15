# Use an official Python runtime based on Debian 10 ("buster") as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the 'app' directory contents into the container at /app
COPY . .

# Copy config.py and requirements.txt into the container
COPY app/config.py .
COPY requirements.txt .

# Copy the wait-for-postgres.sh script into the image
COPY wait_for_postgres.sh /wait_for_postgres.sh

# Make the script executable
RUN chmod +x /wait_for_postgres.sh

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libpq-dev
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80
# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0

# Add the current directory to Python's module search path
ENV PYTHONPATH=${PYTHONPATH}:/app

# Run app.py when the container launches
CMD ["/wait_for_postgres.sh", "postgres", "flask run --host=0.0.0.0"]