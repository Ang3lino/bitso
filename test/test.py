import os
import pytest
import requests
import csv
from unittest import mock
from datetime import datetime
from dags.spread_functions import *
import logging


books = ["btc_mxn", "usd_mxn"]
ticker = fetch_ticker_data(books[0])

@pytest.fixture
def mock_response():
    return {
        "success": True,
        "payload": {
            "created_at": "2024-07-14T10:00:00+00:00",
            "book": "btc_mxn",
            "bid": "790000.00",
            "ask": "800000.00"
        }
    }

@pytest.fixture
def spread_record():
    return {
        "orderbook_timestamp": "2024-07-14T10:00:00+00:00",
        "book": "btc_mxn",
        "bid": 790000.00,
        "ask": 800000.00,
        "spread": 1.25
    }


def test_fetch_ticker_data(mocker, mock_response):
    mock_get = mocker.patch('requests.get')
    mock_get.return_value.json.return_value = mock_response
    
    result = fetch_ticker_data("btc_mxn")
    assert result == mock_response

def test_compute_spread(mock_response):
    data = mock_response['payload']
    result = compute_spread(data)
    expected = {
        "orderbook_timestamp": "2024-07-14T10:00:00+00:00",
        "book": "btc_mxn",
        "bid": 790000.00,
        "ask": 800000.00,
        "spread": 1.25
    }
    assert result == expected

def test_prepare_dir(spread_record, tmp_path):
    base_path = tmp_path / "bucket"
    base_path.mkdir()
    
    file_path, file_exists = prepare_dir(spread_record, base_path)
    
    timestamp = datetime.strptime(spread_record["orderbook_timestamp"], "%Y-%m-%dT%H:%M:%S%z")
    year = timestamp.strftime("%Y")
    month = timestamp.strftime("%m")
    day = timestamp.strftime("%d")
    hour = timestamp.strftime("%H")
    expected_dir = base_path / f"year={year}" / f"month={month}" / f"day={day}" / f"hour={hour}"
    expected_file = expected_dir / "data.csv"
    
    assert file_path == str(expected_file)
    assert file_exists == False
    assert os.path.isdir(expected_dir)


url = "http://127.0.0.1:8000/store_spread"
headers = {
    "Content-Type": "application/json"
}
data = {
    "orderbook_timestamp": "2024-07-14T12:00:00+00:00",
    "book": "btc_mxn",
    "bid": 790000.00,
    "ask": 800000.00,
    "spread": 1.10
}
response = requests.post(url, headers=headers, json=data)
print(response)
response = requests.post('http://127.0.0.1:8000/load_spreads', )
print(response)
