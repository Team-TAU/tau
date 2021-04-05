#!/bin/bash
# set -a; source /code/.env; set +a
export $(grep -v '#.*' .env | xargs)
