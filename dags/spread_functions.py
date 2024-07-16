import requests
import os
import csv
import typing
from datetime import datetime
from tqdm import tqdm

def fetch_ticker_data(book: str) -> dict:
    """
    Fetches ticker data from the Bitso API for a specific book.
    
    Parameters:
        book (str): The trading pair book (e.g., 'btc_mxn', 'usd_mxn').
    
    Returns:
        dict: JSON response containing ticker data.
    """
    url = f"https://sandbox.bitso.com/api/v3/ticker/?book={book}"
    response = requests.get(url)
    data = response.json()
    return data

def compute_spread(data: dict) -> dict:
    """
    Computes the bid-ask spread percentage from ticker data.
    
    Parameters:
        data (dict): Ticker data from the Bitso API.
    
    Returns:
        dict: Spread information including timestamp, book, bid, ask, and spread percentage.
    """
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

def prepare_dir(record: dict, base_path: str) -> typing.Tuple[str, bool]:
    """
    Prepares and creates directory structure based on the timestamp of the record.
    
    Parameters:
        record (dict): Record containing orderbook information.
        base_path (str): Base directory path for storing data.
    
    Returns:
        tuple: File path and boolean indicating if file exists.
    """
    timestamp = datetime.strptime(record["orderbook_timestamp"], "%Y-%m-%dT%H:%M:%S%z")
    year = timestamp.strftime("%Y")
    month = timestamp.strftime("%m")
    day = timestamp.strftime("%d")
    hour = timestamp.strftime("%H")
    
    directory_path = os.path.join(base_path, f"year={year}", f"month={month}", f"day={day}", f"hour={hour}")
    os.makedirs(directory_path, exist_ok=True)
    
    file_path = os.path.join(directory_path, f"data.csv")
    file_exists = os.path.isfile(file_path)
    
    return file_path, file_exists

def save_to_partitioned_directory(records: typing.List[dict], base_path: str) -> None:
    """
    Saves records to partitioned directories in CSV format.
    
    Parameters:
        records (list): List of records to save.
        base_path (str): Base directory path for storing data.
    """
    for record in tqdm(records):
        file_path, file_exists = prepare_dir(record, base_path)
        print(f'Saved in {file_path}')
        
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
            
            if not file_exists:
                writer.writerow(["orderbook_timestamp", "book", "bid", "ask", "spread"])
            
            # Convert bid, ask, and spread to float and write to CSV
            record_f = lambda k: float(record[k])
            bid, ask, spread = record_f('bid'), record_f('ask'), record_f('spread')
            writer.writerow([record["orderbook_timestamp"], record["book"], bid, ask, spread])
