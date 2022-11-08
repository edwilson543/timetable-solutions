# Pull official base image
FROM --platform=linux/amd64 python:3.11-slim-buster

# Set the working directory
WORKDIR /timetable_scheduling

# Set the environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=base_files.settings.production

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
# No cache ensure each build installs the python dependencies fresh
RUN pip3 install -r requirements.txt --no-cache-dir
