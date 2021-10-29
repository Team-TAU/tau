#!/bin/bash
./wait_for_postgres.py && \
./manage.py migrate && \
./manage.py collect_dashboard && \
./manage.py collectstatic --noinput && \
./manage.py import_helix_endpoints helix_endpoints.json && \
./manage.py import_eventsub_subscriptions eventsub_subscriptions.json && \
/usr/local/bin/supervisord -n -c /etc/supervisord.conf
