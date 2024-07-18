alias d=docker
alias dc=docker-compose

# https://stackoverflow.com/questions/32612650/how-to-get-docker-compose-to-always-re-create-containers-from-fresh-images
dc down 
dc build --no-cache
dc up airflow-init
dc -f compose.yml up -d

dc -f compose.yml up -d
dc compose.yml down 

docker-compose -f compose.yml up -d
docker-compose build --no-cache
docker-compose up -d --no-deps --build postgres

CONTAINER_NAME='bitso-webserver-1'
d ps -a
d ps -ad
d exec -it $CONTAINER_NAME bash
docker exec -it --user root $CONTAINER_NAME /bin/bash


psql --host host.docker.internal -U airflow
psql --host host.docker.internal -U airflow -d batch

export PGPASSWORD='airflow'
psql -h host.docker.internal -d airflow -U airflow -p 5432 -a -q -f ./sql/drop_batch_db.sql
psql -h host.docker.internal -d airflow -U airflow -p 5432 -a -q -f ./sql/create_db.sql
psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/old_model.sql
psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/copy.sql  # when using \copy the entire stmt must be in one line
psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/new_model.sql
psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/migration.sql

psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/truncate.sql
# psql -h host.docker.internal -d batch -U airflow -p 5432 -a -q -f ./sql/queries.sql



pg_dump -h host.docker.internal -p 5432 -d old  -U airflow -s -F p -E UTF-8 -f ./out_schema.sql

uvicorn server.main:app --host "0.0.0.0" --reload

curl -X POST -H "Content-Type: application/json" -d "'$req'" $url
curl -X POST -H "Content-Type: application/json" -d '{"orderbook_timestamp": "2024-07-14T10:00:00+00:00", "book": "btc_mxn", "bid": 790000.00, "ask": 800000.00, "spread": 1.25}' 'http://127.0.0.1:8000/store_spread'
curl -X POST 'http://127.0.0.1:8000/load_spreads'

airflow dags list
airflow connections add 'http_default'     --conn-type 'http'     --conn-host 'http://127.0.0.1:8000'
airflow dags list-runs --dag-id post_spread_data
airflow connections delete 'http_default'
airflow connections add 'http_default'     --conn-type 'http'     --conn-host 'http://127.0.0.1:8000'
airflow dags list
airflow dags trigger post_spread_data

airflow connections add 'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'host.docker.internal' \
    --conn-schema 'batch' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-port '5432'
