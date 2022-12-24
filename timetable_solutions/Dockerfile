# Pull official base image
FROM --platform=linux/amd64 python:3.11-slim-buster

# Set the environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=base_files.settings.production

# Set the working directory and create other necessary directories
ENV HOME=/home/app
ENV APP_HOME=$HOME/web
RUN mkdir -p $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

# Install dependencies (note we don't install the test suite dependencies)
COPY ./timetable_solutions/app-requirements.txt app-requirements.txt
RUN pip install --upgrade pip
RUN pip install -r app-requirements.txt

# Copy over the full django project
COPY ./timetable_solutions $APP_HOME

# Add a non-root 'app' user to group 'app'
RUN groupadd app
RUN useradd app -g app

# Chown all files to the non-root app user (transfer ownership)
RUN chown -R app:app $APP_HOME

# Change user to the app user
USER app
