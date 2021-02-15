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

# Adds our application code to the image
COPY . /code
WORKDIR /code


EXPOSE 8000

# # Migrates the database, uploads staticfiles, and runs the production server
# CMD ./manage.py migrate && \
#     ./manage.py collectstatic --noinput && \
#     ./manage.py runserver 0.0.0.0:8000

CMD ./manage.py migrate && \
    /usr/bin/supervisord