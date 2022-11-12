# Pull official base image
FROM --platform=linux/amd64 python:3.11-slim-buster

# Set the environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=base_files.settings.production

# Set the working directory
WORKDIR /timetable_scheduling


# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./timetable_solutions .
