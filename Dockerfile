FROM python:3.11-slim-buster
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=base_files.settings.production
WORKDIR /timetable_scheduling
COPY requirements.txt requirements.txt
# No cache ensure each build installs the python dependencies fresh
RUN pip3 install -r requirements.txt --no-cache-dir
