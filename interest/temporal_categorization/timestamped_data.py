"""
This module provides classes and utilities for working with data
that includes timestamps.
"""
import json
from datetime import datetime
from pathlib import Path


class TimestampedData:
    """
    Represents data with a timestamp.

    Attributes:
        DATE_FIELD (str): The field name for the timestamp in the data.
        _filename (Path): The path to the file containing the data.
        _data (dict): The loaded JSON data.
        _timestamp (datetime): The timestamp extracted from the data.

    Methods:
        __init__(self, filename): Initializes the TimestampedData object.
        filename(self) -> Path: Returns the filename path.
        _load_data(self): Loads data from the file.
        _get_timestamp(self): Extracts the timestamp from the data.
        categorize(self): Abstract method for categorizing data by timestamp.
    """

    DATE_FIELD = "Date"

    def __init__(self, filename: Path):
        """
        Initializes the TimestampedData object.

        Args:
            filename (Path): The path to the file containing the data.
        """
        self._filename = filename
        self._data = self._load_data()
        self._timestamp = self._get_timestamp()

    @property
    def filename(self) -> Path:
        """
        Returns the filename path.

        Returns:
            Path: The filename path.
        """
        return self._filename

    def _load_data(self):
        """
        Loads data from the file.

        Returns:
            dict: The loaded JSON data.
        """
        with open(self._filename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def data(self):
        """
        Returns the json data

        Returns:
            dict: The loaded JSON data.
        """
        return self._data

    def _get_timestamp(self):
        """
        Extracts the timestamp from the data.

        Returns:
            datetime: The extracted timestamp.
        """
        return datetime.strptime(self._data[self.DATE_FIELD], '%Y-%m-%d')

    def categorize(self):
        """
        Abstract method for categorizing data by timestamp.

        Raises:
            NotImplementedError: Subclasses must implement categorize method.
        """
        raise NotImplementedError("Subclass must implement categorize method")


class YearPeriodData(TimestampedData):
    """
    Represents data categorized by year.

    Methods:
        categorize(self): Categorizes data by year.
    """

    def categorize(self):
        """
        Categorizes data by year.

        Returns:
            int: The year of the timestamp.
        """
        return self._timestamp.year


class DecadePeriodData(TimestampedData):
    """
    Represents data categorized by decade.

    Methods:
        categorize(self): Categorizes data by decade.
    """

    def categorize(self):
        """
        Categorizes data by decade.

        Returns:
            int: The decade of the timestamp.
        """
        year = self._timestamp.year
        return (year // 10) * 10
