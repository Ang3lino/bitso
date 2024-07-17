import os
import csv
import pandas as pd
import great_expectations as ge
import messytables
from messytables import CSVTableSet, type_guess, types_processor

# os.listdir()
# print(os.path.dirname(os.path.realpath(__file__)))


def extract_headers(file_path):
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        headers = next(csv_reader)
        return headers

def get_rpath_from(dir_name: str):
    return [os.path.join(dir_name, fpath) for fpath in os.listdir(dir_name)]


relative_path = os.path.join('02', 'bucket')
f_names = os.listdir(relative_path)
f_names.sort()
tables = [
    (fname, pd.read_csv(os.path.join(relative_path, fname)))
    for fname in f_names
]

from pprint import pprint
for k, v in tables:
    print(k)
    pprint(v.head())