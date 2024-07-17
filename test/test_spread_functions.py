import os
import pytest
import sys

from unittest.mock import patch, mock_open


# we expect to run this outside the current script location to use same helper functions
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)


from dags.spread_functions import fetch_ticker_data, compute_spread, prepare_dir, save_to_partitioned_directory
# import requests
# from datetime import datetime


# Mock response for fetch_ticker_data
class MockResponse:
    @staticmethod
    def json():
        return {
            'book': 'btc_mxn',
            'created_at': '2024-07-15T08:23:30+00:00',
            'bid': '1023069.98',
            'ask': '1023070.02'
        }


@pytest.fixture
def mock_ticker_data():
    return {
        'book': 'btc_mxn',
        'created_at': '2024-07-15T08:23:30+00:00',
        'bid': '1023069.98',
        'ask': '1023070.02'
    }

@pytest.fixture
def mock_spread_data():
    return {
        'book': 'btc_mxn',
        'orderbook_timestamp': '2024-07-15T08:23:30+00:00',
        'bid': 1023069.98,
        'ask': 1023070.02,
        'spread': 0.0002
    }

def test_fetch_ticker_data(mocker):
    mocker.patch('requests.get', return_value=MockResponse())
    data = fetch_ticker_data('btc_mxn')
    assert data['book'] == 'btc_mxn'
    assert data['created_at'] == '2024-07-15T08:23:30+00:00'

def test_compute_spread(mock_ticker_data):
    spread_data = compute_spread(mock_ticker_data)
    assert spread_data['book'] == 'btc_mxn'
    assert spread_data['orderbook_timestamp'] == '2024-07-15T08:23:30+00:00'
    assert spread_data['bid'] == 1023069.98
    assert spread_data['ask'] == 1023070.02
    assert spread_data['spread'] == pytest.approx((1023070.02 - 1023069.98) * 100 / 1023070.02)

def test_prepare_dir(mocker):
    mocker.patch('os.makedirs')
    base_path = '/tmp'
    book = 'btc_mxn'
    record = {
        "orderbook_timestamp": "2024-07-15T08:23:30+00:00",
        "book": book,
        "bid": 1023069.98,
        "ask": 1023070.02,
        "spread": 3.909800820598076e-06
    }
    expected_file_path = os.path.join(base_path, 'year=2024', 'month=07', 'day=15', 'hour=08', f'book={book}', 'data.csv')
    file_path, file_exists = prepare_dir(record, base_path, book)
    assert file_path == expected_file_path
    assert file_exists is False  # Assuming the file does not exist

def test_save_to_partitioned_directory(mocker, mock_spread_data):
    mocker.patch('os.makedirs')
    mocker.patch('os.path.isfile', return_value=False)
    mocker.patch('builtins.open', new_callable=mock_open)
    base_path = '/tmp'
    book = 'btc_mxn'
    records = [mock_spread_data]

    save_to_partitioned_directory(records, base_path, book)
    open.assert_called_once_with(os.path.join(base_path, 'year=2024', 'month=07', 'day=15', 'hour=08', f'book={book}', 'data.csv'), 'a', newline='', encoding='utf-8')

    handle = open()
    handle.write.assert_called()  # Ensure that write was called
