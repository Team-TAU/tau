FROM python:3.8
ENV PYTHONUNBUFFERED 1

# Install supervisord
RUN apt-get update && apt-get install -y supervisor

RUN mkdir -p /var/log/supervisor

# Allows docker to cache installed dependencies between builds
COPY requirements.txt /tmp/pip-tmp/requirements.txt
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp
run pip install -r /tmp/pip-tmp/requirements.txt
run rm -rf /tmp/pip-tmp

COPY supervisord.conf /etc/supervisord.conf

# Adds our application code to the image
COPY . /code

# Adds loadenv to profile.d
COPY ./scripts/loadenv.sh /root/.bashrc

# Sets work directory to /code
WORKDIR /code

EXPOSE $PORT

CMD bash -c "source ./scripts/loadenv.sh && \
    ./manage.py migrate && \
    ./manage.py collectstatic --noinput && \
    /usr/bin/supervisord -n -c /etc/supervisord.conf"

