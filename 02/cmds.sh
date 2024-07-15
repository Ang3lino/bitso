
docker-compose -f postgres_comp.yml up -d
docker exec -it 02-db-1 bash
psql -U postgres --password