# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /srv/webapp
WORKDIR /srv/webapp

# Copy msc
COPY ./msc ./msc

WORKDIR /srv/webapp/msc

RUN ls -l /srv/webapp/msc
RUN pwd

RUN apt update && \
    apt install -y --no-install-recommends build-essential libpq-dev python3-dev

RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install fastapi uvicorn

# Make port 8000 available to the world outside this container
EXPOSE 8000

WORKDIR /srv/webapp

# Copy files
COPY ./alembic ./alembic
COPY ./alembic.ini ./docker/docker-entrypoint.sh ./pytest.ini ./

# Run app.py when the container launches
CMD ["uvicorn", "--proxy-headers", "msc.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips='*'"]