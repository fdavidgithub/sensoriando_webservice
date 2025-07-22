#!/bin/sh

python manage.py makemigrations
python manage.py migrate --noinput
exec python manage.py runserver 0.0.0.0:$DJANGO_PORT $DJANGO_PARAMS

