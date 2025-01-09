"""
This script defines functions and classes to categorize files based
on their timestamps.
"""
import argparse
import logging
from typing import Iterable
from pathlib import Path
import pandas as pd
from tqdm import tqdm  # type: ignore
from dataQuest.temporal_categorization import PERIOD_TYPES
from dataQuest.temporal_categorization.timestamped_data import TimestampedData

OUTPUT_FILE_NAME = 'articles'
FILENAME_COLUMN = 'file_path'
ARTICLE_ID_COLUMN = 'article_id'


def categorize_articles(
    input_dir: Path,
    period_type: str,
    glob_pattern: str,
    output_dir: Path,
):
    """
    Core functionality to categorize articles by timestamp.

    Args:
        input_dir (Path): Directory containing input files.
        period_type (str): Type of time period to use for categorization.
        glob_pattern (str): Glob pattern to find input files (e.g., '*.json').
        output_dir (Path): Directory to save categorized files.
    """
    if not input_dir.is_dir():
        raise ValueError(f"Not a directory: '{str(input_dir.absolute())}'")

    time_period_class = PERIOD_TYPES[period_type]
    timestamped_objects: Iterable[TimestampedData] = [
        time_period_class(path) for path in input_dir.rglob(glob_pattern)
    ]

    output_dir.mkdir(parents=True, exist_ok=True)

    for timestamped_object in tqdm(timestamped_objects,
                                   desc="Categorize by timestamp",
                                   unit="file"):
        try:
            timestamp = timestamped_object.categorize()
            timestamp_file_name = output_dir / f"{OUTPUT_FILE_NAME}_{timestamp}.csv"

            if timestamp_file_name.exists():
                df = pd.read_csv(timestamp_file_name)
            else:
                df = pd.DataFrame(columns=[FILENAME_COLUMN, ARTICLE_ID_COLUMN])

            new_row = {
                FILENAME_COLUMN: str(timestamped_object.data()[FILENAME_COLUMN]),
                ARTICLE_ID_COLUMN: str(timestamped_object.data()[ARTICLE_ID_COLUMN]),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            df.to_csv(timestamp_file_name, index=False)

        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error processing timestamped object: %s", str(e))


def cli():
    """
        Command-line interface for categorize articles by timestamp.
    """
    parser = argparse.ArgumentParser("Categorize articles by timestamp.")

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Base directory for reading input files.",
    )
    parser.add_argument(
        "--period-type",
        type=str,
        required=True,
        choices=list(PERIOD_TYPES.keys()),
        help="Time periods",
    )
    parser.add_argument(
        "--glob",
        type=str,
        required=True,
        default="*.json",
        help="Glob pattern for find input files; e.g. '*.json'.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="The directory for storing output files.",
    )

    args = parser.parse_args()

    try:
        categorize_articles(
            input_dir=args.input_dir,
            period_type=args.period_type,
            glob_pattern=args.glob,
            output_dir=args.output_dir,
        )
    except ValueError as e:
        parser.error(str(e))
    except Exception as e:  # pylint: disable=broad-except
        logging.error("Error occurred in CLI: %s", str(e))


if __name__ == "__main__":
    cli()
