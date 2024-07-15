
from typing import Union
from fastapi import FastAPI
from pprint import pprint
# from fastapi import Request, FastAPI
# from starlette.requests import Request
# from starlette.responses import Response
from pydantic import BaseModel

from dags.spread_functions import *


class Spread(BaseModel):
    orderbook_timestamp: str
    book: str 
    bid: float
    ask: float
    spread: float 


app = FastAPI()
buffer = []


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/store_spread")
async def store_spread(spread: Spread):
    buffer.append(spread)
    return buffer

@app.post("/load_spreads")
# async def load_spreads(base_path: str):
async def load_spreads():
    base_path = '/opt/airflow/bucket/get_ticker'
    res = {'success': True} 
    for i, s in enumerate(buffer):
        buffer[i] = dict(s)
    # try:
    save_to_partitioned_directory(buffer, base_path)
    buffer.clear()
    # return {'success': True, 'info': saved_in} 
    # except Exception as e:
    #     return {'success': False, 'info': e} 
    return res