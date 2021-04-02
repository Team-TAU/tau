FROM python:3.8
ENV PYTHONUNBUFFERED 1

ARG REDIS='external'

# Install supervisord
RUN apt-get update && apt-get install -y supervisor
RUN if [ "${REDIS}" != "external" ]; then apt-get update && apt-get install -y redis-server; fi

RUN mkdir -p /var/log/supervisor

# Allows docker to cache installed dependencies between builds
COPY requirements.txt /tmp/pip-tmp/requirements.txt
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp
run pip install -r /tmp/pip-tmp/requirements.txt
run rm -rf /tmp/pip-tmp

# Adds our application code to the image
COPY . /code
WORKDIR /code

RUN if [ "${REDIS}" != "external" ]; then cp /code/supervisord-redis.conf /etc/supervisord.conf; else cp /code/supervsiord.conf /etc/supervsiord.conf; fi

CMD ./manage.py migrate && \
    ./manage.py collectstatic --noinput && \
    /usr/bin/supervisord -n -c /etc/supervisord.conf

