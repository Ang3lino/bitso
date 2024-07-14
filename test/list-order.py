
# import bitso
import csv
import os
import requests
import time

from pprint import pprint
from datetime import datetime
from tqdm import tqdm


def fetch_order_book(book):
    url = f"https://sandbox.bitso.com/api/v3/order_book/?book={book}"
    response = requests.get(url)
    data = response.json()
    return data

def compute_spread(data):
    best_ask = float(min(data['asks'], key=lambda x: float(x['price']))['price'])
    best_bid = float(max(data['bids'], key=lambda x: float(x['price']))['price'])
    spread = (best_ask - best_bid) * 100 / best_ask
    return {
        "orderbook_timestamp": data['updated_at'],
        "book": data['asks'][0]['book'],  # Assuming all entries in 'asks' and 'bids' have the same 'book' value
        "bid": best_bid,
        "ask": best_ask,
        "spread": spread
    }

def save_to_partitioned_directory(record, base_path):
    timestamp = datetime.strptime(record["orderbook_timestamp"], "%Y-%m-%dT%H:%M:%S%z")  # obtain timestamp and extract their times to partitionate
    year = timestamp.strftime("%Y")
    month = timestamp.strftime("%m")
    day = timestamp.strftime("%d")
    hour = timestamp.strftime("%H")
    # create a directory which mimics S3 partition file
    directory_path = os.path.join(base_path, f"year={year}", f"month={month}", f"day={day}", f"hour={hour}")
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, f"data.csv")
    file_exists = os.path.isfile(file_path)
    # write the file
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
        if not file_exists:
            writer.writerow(["orderbook_timestamp", "book", "bid", "ask", "spread"])
        writer.writerow([record["orderbook_timestamp"], record["book"], record["bid"], record["ask"], record["spread"]])


books = ["mxn_btc", 'usd_mxn']
book = books[0]
base_path = "./bucket"


for it in tqdm(range(10)):
    time.sleep(1)
    order_book_data = fetch_order_book(book)
    if order_book_data is not None and order_book_data['success']:
        payload = order_book_data['payload']
        record = compute_spread(payload)
        pprint(record)
        save_to_partitioned_directory(record, base_path)

