FROM python:3.11
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=base_files.settings.production
WORKDIR /timetable_scheduling
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
