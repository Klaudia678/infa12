import csv
from datetime import datetime
from typing import TextIO


class CSVWriter:
    CSV_DIR = '../results/'
    csv_files: dict[str, TextIO] = {}

    def __init__(self, headers: list[str], filename=''):
        full_path = CSVWriter.CSV_DIR + filename
        self.full_path = full_path
        if full_path not in CSVWriter.csv_files.keys():
            csv_file = open(full_path + datetime.now().strftime('%Y_%m_%d_%H_%M') + '.csv', 'w', newline='')
            csv.DictWriter(csv_file, fieldnames=headers).writeheader()
            CSVWriter.csv_files[full_path] = csv_file

    def save_row(self, values: dict) -> None:
        csv_file = CSVWriter.csv_files[self.full_path]
        csv_writer = csv.DictWriter(csv_file, fieldnames=values.keys())
        try:
            csv_writer.writerow({x: '{:.3f}'.format(y) for x, y in values.items()})
        except Exception as e:
            csv_writer.writerow(values)
        csv_file.flush()
