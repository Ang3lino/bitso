
from typing import Union
from fastapi import FastAPI
from pprint import pprint
from pydantic import BaseModel
from dags.spread_functions import *
# from fastapi import Request, FastAPI
# from starlette.requests import Request
# from starlette.responses import Response

import logging


app = FastAPI()
buffer = []

class Spread(BaseModel):
    orderbook_timestamp: str
    book: str 
    bid: float
    ask: float
    spread: float 


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/store_spread")
async def store_spread(spread: Spread):
    'This functions writes on buffer'
    global buffer
    logging.info(f"Reveived spread {spread}.")
    buffer.append(spread)
    return buffer

@app.post("/load_spreads")
async def load_spreads():
    'This functions reads from buffer and flush it'
    global buffer
    base_path = '/opt/airflow/bucket/get_ticker'
    res = {'success': True, 'spreads_processed': len(buffer)} 
    logging.info(f"About to write {len(buffer)} records.")
    if buffer:
        for i, s in enumerate(buffer): # save expects List[dict]
            buffer[i] = dict(s)
        save_to_partitioned_directory(buffer, base_path)
        buffer.clear()
    return res
