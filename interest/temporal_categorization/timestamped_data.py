import json
from datetime import datetime
from pathlib import Path


class TimestampedData:
    DATE_FIELD = "Date"

    def __init__(self, filename):
        self._filename = filename
        self._data = self._load_data()
        self._timestamp = self._get_timestamp()

    @property
    def filename(self) -> Path:
        return self._filename

    def _load_data(self):
        with open(self._filename, 'r') as file:
            return json.load(file)

    def _get_timestamp(self):
        return datetime.strptime(self._data[self.DATE_FIELD], '%Y-%m-%d')

    def categorize(self):
        raise NotImplementedError("Subclasses must implement categorize method")


class YearPeriodData(TimestampedData):
    def categorize(self):
        return self._timestamp.year


class DecadePeriodData(TimestampedData):
    def categorize(self):
        year = self._timestamp.year
        return (year // 10) * 10
