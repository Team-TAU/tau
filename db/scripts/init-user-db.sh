#!/bin/bash
set -e
declare -a errors=()

if [[ -z "${DJANGO_DB_TYPE}" ]]; then
    errors+=( "No DJANGO_DB_TYPE variable set. Must be set to \"postgres\" or \"sqlite3\"" )  
fi

if [[ "${DJANGO_DB_TYPE}" -eq "postgres" ]]; then
    if [[ -z "${DJANGO_DB}" ]]; then
        errors+=( "No DJANGO_DB variable set (Django Database Name)" )
    fi
    if [[ -z "${DJANGO_DB_USER}" ]]; then
        errors+=(   "No DJANGO_DB_USER variable set (Django Database Username)" )
    fi
else
    if [[ "${DJANGO_DB_TYPE}" -eq "sqlite3" ]]; then
        echo "Using sqlite3"
        exit 0
    fi
fi
cnt=${#errors[@]}    
if [[ cnt -gt 0 ]]; then
    for (( i = 0 ; i < cnt ; i++ ))
    do
        echo "[ERROR]: ${errors[$i]}"
    done
    exit 1
fi
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $DJANGO_DB_USER WITH ENCRYPTED PASSWORD '$DJANGO_DB_PW';
    CREATE DATABASE $DJANGO_DB;
    GRANT ALL PRIVILEGES ON DATABASE $DJANGO_DB TO $DJANGO_DB_USER;
EOSQL

