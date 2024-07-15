alias d=docker
alias dc=docker-compose

dc -f compose.yml up -d
docker-compose -f compose.yml up -d
dc compose.yml down 

d ps -a
d ps -ad

docker-compose build --no-cache
d exec -it bitso-webserver-1 bash

uvicorn server.main:app --host "0.0.0.0" --reload

curl -X POST -H "Content-Type: application/json" -d "'$req'" $url
curl -X POST -H "Content-Type: application/json" -d '{"orderbook_timestamp": "2024-07-14T10:00:00+00:00", "book": "btc_mxn", "bid": 790000.00, "ask": 800000.00, "spread": 1.25}' 'http://127.0.0.1:8000/store_spread'
curl -X POST 'http://127.0.0.1:8000/load_spreads'