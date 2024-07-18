#!/bin/bash

pip install -r /requirements.txt
pytest test/test_spread_functions.py

# Run SQL scripts
export PGPASSWORD='airflow'
psql -h host.docker.internal -d airflow -U airflow -p 5432 -a -q -f ./sql/create_db.sql
psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/old_model.sql
psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/copy.sql
psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/new_model.sql
psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/migration.sql

# Add the new postgres connection
airflow connections add 'postgres_default' \
  --conn-type 'postgres' \
  --conn-host 'host.docker.internal' \
  --conn-schema 'batch' \
  --conn-login 'airflow' \
  --conn-password 'airflow' \
  --conn-port '5432'

# Execute the CMD from Dockerfile
# exec "$@"
