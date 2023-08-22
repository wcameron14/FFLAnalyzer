# Use an official Python runtime based on Debian 10 ("buster") as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the 'app' directory contents into the container at /app
COPY . .

# Copy config.py and requirements.txt into the container
COPY app/config.py .
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libpq-dev wget
RUN pip install --no-cache-dir -r requirements.txt

# Set Dockerize environment variables.
ENV DOCKERIZE_VERSION v0.6.1
# Download and install Dockerize
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

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
CMD dockerize -wait tcp://postgres:5432 -timeout 1m flask run --host=0.0.0.0