FROM python:3.10.5

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

RUN apt-get update && apt-get install -y netcat
COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini


RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt
     
COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ./entrypoint.sh

