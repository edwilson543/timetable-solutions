# Pull official base image
FROM --platform=linux/amd64 python:3.11-slim-buster

# Set the environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=base_files.settings.production

# Set the working directory and static file directory
RUN mkdir /timetable_scheduling
RUN mkdir /timetable_scheduling/staticfiles
WORKDIR /timetable_scheduling


# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
# No cache ensure each build installs the python dependencies fresh
RUN pip3 install -r requirements.txt --no-cache-dir
