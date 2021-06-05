FROM python:3.8

ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

# install supervisord (supervisor-stdout is not py3 compatible in pypi)
RUN pip install supervisor git+https://github.com/coderanger/supervisor-stdout

# Sets work directory to /code
WORKDIR /code

# Allows docker to cache installed dependencies between builds
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY supervisord.conf /etc/supervisord.conf

# Adds our application code to the image
COPY . /code

CMD bash -c "./scripts/start.sh"
