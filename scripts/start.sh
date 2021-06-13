#!/bin/bash
./wait_for_postgres.py && \
./manage.py migrate && \
./manage.py collectstatic --noinput && \
./manage.py import_helix_endpoints helix_endpoints.json && \
/usr/local/bin/supervisord -n -c /etc/supervisord.conf
