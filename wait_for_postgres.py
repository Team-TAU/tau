#!/usr/bin/env python
"""Command-line utility for db setup."""
import os
import logging
import sys
from time import time, sleep
from psycopg2 import connect, sql, OperationalError
db_type = os.getenv("DJANGO_DB_TYPE", "postgres")
db_user = os.getenv("DJANGO_DB_USER","tau_db")
db_name = os.getenv("DJANGO_DB","tau_db")
db_pw = os.getenv("DJANGO_DB_PW","")
check_timeout = os.getenv("POSTGRES_CHECK_TIMEOUT", 30)
check_interval = os.getenv("POSTGRES_CHECK_INTERVAL", 1)
interval_unit = "second" if check_interval == 1 else "seconds"
config = {
    "dbname": os.getenv("POSTGRES_DB", "postgres"),
    "user": os.getenv(
        "PGUSER",
        os.getenv("POSTGRES_USER", "postgres")
    ),
    "password": os.getenv(
        "PGPASSWORD",
        os.getenv("POSTGRES_PASSWORD", "")
    ),
    "host": os.getenv(
        "PGHOST",
        os.getenv("DJANGO_DB_HOST", "db")
    ),
    "port": os.getenv(
        "PGPORT",
        os.getenv("DJANGO_DB_PORT", 5432)
    )
}

start_time = time()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def pg_isready(host, user, password, dbname, port):
    if db_type != "postgres":
        logger.info("DJANGO_DB_TYPE is not set to \"postgres\". Skipping.")
        return True
    while time() - start_time < check_timeout:
        try:
            conn = connect(**vars())
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS count FROM pg_catalog.pg_user WHERE usename=%s;",(db_user,))
            user_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) AS count FROM pg_database WHERE datname=%s;",(db_name,))
            db_count = cur.fetchone()[0]
            if user_count == 0:
                logger.info(f"Creating user {db_user}")
                add_user_query = f"CREATE USER {db_user} WITH ENCRYPTED PASSWORD '{db_pw}';"
                cur.execute(add_user_query)
                grant_query = f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"
                cur.execute(grant_query)
            else:
                logger.info(f"Found a user {db_user}, updating password to current DJANGO_DB_PW value.")
                update_user_query = f"ALTER USER {db_user} WITH ENCRYPTED PASSWORD '{db_pw}'"
                cur.execute(update_user_query)
            if db_count == 0:
                logger.info(f"Creating database {db_name}")
                add_db_query = f"CREATE DATABASE {db_name};"
                cur.execute(add_db_query)
            logger.info("Postgres is ready!")
            conn.close()
            return True
        except OperationalError:
            logger.info(f"Postgres isn't ready. Waiting for {check_interval} {interval_unit}...")
            sleep(check_interval)

    logger.error(f"We could not connect to Postgres within {check_timeout} seconds.")
    sys.exit(1)
    return False


pg_isready(**config)
