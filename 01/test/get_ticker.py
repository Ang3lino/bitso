import requests
import os
import csv
import time

from datetime import datetime
from tqdm import tqdm
from pprint import pprint


def fetch_ticker_data(book):
    url = f"https://sandbox.bitso.com/api/v3/ticker/?book={book}"
    response = requests.get(url)
    data = response.json()
    return data

def compute_spread(data):
    best_ask = float(data['ask'])
    best_bid = float(data['bid'])
    spread = (best_ask - best_bid) * 100 / best_ask
    return {
        "orderbook_timestamp": data['created_at'],
        "book": data['book'],
        "bid": best_bid,
        "ask": best_ask,
        "spread": spread
    }

def prepare_dir(record, base_path):
    timestamp = datetime.strptime(record["orderbook_timestamp"], "%Y-%m-%dT%H:%M:%S%z")
    year = timestamp.strftime("%Y")
    month = timestamp.strftime("%m")
    day = timestamp.strftime("%d")
    hour = timestamp.strftime("%H")
    # prepare and create dir if needed
    directory_path = os.path.join(base_path, f"year={year}", f"month={month}", f"day={day}", f"hour={hour}")
    os.makedirs(directory_path, exist_ok=True)
    # prepare path used outside function
    file_path = os.path.join(directory_path, f"data.csv")
    file_exists = os.path.isfile(file_path)
    return file_path, file_exists

def save_to_partitioned_directory(record, base_path):
    file_path, file_exists = prepare_dir(record, base_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
        if not file_exists:
            writer.writerow(["orderbook_timestamp", "book", "bid", "ask", "spread"])
        record_f = lambda k: float(record[k])
        bid, ask, spread = record_f('bid'), record_f('ask'), record_f('spread')
        writer.writerow([record["orderbook_timestamp"], record["book"], bid, ask, spread])


BASE_PATH = "./bucket/get_ticker/"
BOOKS = ["btc_mxn", "usd_mxn"]
if __name__ == "__name__":
    for book in BOOKS:
        ticker_data = fetch_ticker_data(book) # extract, fetch data
        if ticker_data and ticker_data['success']: # transform, check if call was success
            pprint(ticker_data)
            payload = ticker_data['payload']
            spread_record = compute_spread(payload)
            print(spread_record)
            save_to_partitioned_directory(spread_record, BASE_PATH) # load, save the file in partition
