#!/bin/bash
./wait_for_postgres.py && \
./manage.py migrate && \
./manage.py collectstatic --noinput && \
/usr/local/bin/supervisord -n -c /etc/supervisord.conf
