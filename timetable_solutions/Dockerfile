# Pull official base image
FROM --platform=linux/amd64 python:3.11-slim-buster

# Set the environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=base_files.settings.production

# Set the working directory
WORKDIR /timetable_scheduling

# Install dependencies (note we don't install the test suit dependencies)
RUN pip install --upgrade pip
COPY ./timetable_solutions/app-requirements.txt app-requirements.txt
RUN pip3 install -r app-requirements.txt
COPY ./timetable_solutions .
