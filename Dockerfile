FROM python:3.8

ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

ARG REDIS='external'

# optionally install REDIS
RUN if [ "${REDIS}" != "external" ]; then apt-get update && apt-get install -y redis-server; fi

# install supervisord (supervisor-stdout is not py3 compatible in pypi)
RUN pip install supervisor git+https://github.com/coderanger/supervisor-stdout

# Sets work directory to /code
WORKDIR /code

# Allows docker to cache installed dependencies between builds
COPY requirements.txt .
RUN pip install -r requirements.txt

# Adds our application code to the image
COPY . /code

# configure for redis
RUN if [ "${REDIS}" != "external" ]; then cp supervisord-redis.conf /etc/supervisord.conf; else cp supervisord.conf /etc/supervisord.conf; fi

CMD bash -c "./manage.py migrate && \
    ./manage.py collectstatic --noinput && \
    /usr/local/bin/supervisord -n -c /etc/supervisord.conf"
