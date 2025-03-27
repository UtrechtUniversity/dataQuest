"""
This script filter articles from input files according to
specified configurations.
"""

import argparse
import logging
from pathlib import Path
from typing import Iterable, List
import pandas as pd
from tqdm import tqdm

from dataQuest.filter import INPUT_FILE_TYPES
from dataQuest.filter.input_file import InputFile
from dataQuest.utils import load_filters_from_config
from dataQuest.utils import save_filtered_articles
from dataQuest.temporal_categorization import PERIOD_TYPES
from dataQuest.temporal_categorization.timestamped_data import TimestampedData
from dataQuest.utils import get_keywords_from_config
from dataQuest.utils import read_config
from dataQuest.article_final_selection.process_articles import select_articles
from dataQuest.generate_output import generate_output

ARTICLE_SELECTOR_FIELD = "article_selector"
OUTPUT_FILE_NAME = 'articles'
FILENAME_COLUMN = 'file_path'
ARTICLE_ID_COLUMN = 'article_id'


def filter_articles(
    input_dir: Path,
    glob_pattern: str,
    config_path: Path,
    input_type: str,
    output_dir: Path,
):
    """
    Core functionality to process files, filter articles, and save results.

    Args:
        input_dir (Path): Directory containing input files.
        glob_pattern (str): Glob pattern to match input files.
        config_path (Path): Path to the configuration file.
        input_type (str): File format of the input files.
        output_dir (Path): Directory to save filtered articles.
    """
    if not input_dir.is_dir():
        raise ValueError(f"Not a directory: '{str(input_dir.absolute())}'")

    input_file_class = INPUT_FILE_TYPES[input_type]
    input_files: Iterable[InputFile] = [
        input_file_class(path) for path in input_dir.rglob(glob_pattern)
    ]

    output_dir.mkdir(parents=True, exist_ok=True)

    compound_filter = load_filters_from_config(config_path)

    for input_file in tqdm(input_files, desc="Filtering articles", unit="file"):
        for article in input_file.selected_articles(compound_filter):
            save_filtered_articles(input_file, article.id, output_dir)


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

            expected_columns = [FILENAME_COLUMN, ARTICLE_ID_COLUMN]

            if timestamp_file_name.exists():
                df = pd.read_csv(timestamp_file_name)
            else:
                df = pd.DataFrame(columns=expected_columns)

            new_row = {
                FILENAME_COLUMN: str(timestamped_object.data().get(FILENAME_COLUMN, "")),
                ARTICLE_ID_COLUMN: str(timestamped_object.data().get(ARTICLE_ID_COLUMN, ""))
            }
            df = pd.concat([df, pd.DataFrame([new_row], columns=expected_columns)],
                           ignore_index=True)

            df.to_csv(timestamp_file_name, index=False)

        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error processing timestamped object: %s", str(e))


def update_selected_indices_in_file(filepath: str,
                                    indices_selected: List[int]) -> None:
    """
    Update selected indices in a CSV file.

    Args:
        filepath (str): The path to the CSV file.
        indices_selected (List[int]): A list of indices to be marked
        as selected.

    Raises:
        ValueError: If indices_selected is empty or contains
        non-negative integers.

    """
    try:
        if indices_selected and all(isinstance(idx, int) and idx >= 0
                                    for idx in indices_selected):
            df = pd.read_csv(filepath)
            df['selected'] = 0
            df.loc[indices_selected, 'selected'] = 1
            df.to_csv(filepath, index=False)
        else:
            raise ValueError("Invalid indices_selected")
    except Exception as e:  # pylint: disable=W0718
        logging.error("Error updating selected indices in file: %s",
                      e)


def select_final_articles(
    input_dir: Path,
    glob_pattern: str,
    config_path: Path,
):
    """
    Core functionality to select final articles based on keywords and configuration.

    Args:
        input_dir (Path): Directory containing input files.
        glob_pattern (str): Glob pattern to match input files (e.g., '*.csv').
        config_path (Path): Path to the configuration file.
    """
    if not input_dir.is_dir():
        raise ValueError(f"Not a directory: '{str(input_dir.absolute())}'")

    keywords = get_keywords_from_config(config_path)
    config_article_selector = read_config(config_path, ARTICLE_SELECTOR_FIELD)

    if len(keywords) > 0 and config_article_selector:
        for articles_filepath in tqdm(
            input_dir.rglob(glob_pattern),
            desc="Processing articles",
            unit="file",
        ):
            try:
                selected_indices = select_articles(
                    str(articles_filepath), keywords, config_article_selector
                )

                update_selected_indices_in_file(str(articles_filepath), selected_indices)
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Error processing file %s: %s", articles_filepath, str(e))


def cli():
    """
        Command-line interface for filter articles.
    """
    parser = argparse.ArgumentParser("Filter articles from input files.")

    parser.add_argument(
        "--input-dir",
        type=Path,
        help="Base directory for reading input files. ",
    )
    parser.add_argument(
        "--glob",
        type=str,
        required=True,
        help="Glob pattern for find input files; e.g. '*.gz' ",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        default="config.json",
        help="File path of config file.",
    )
    parser.add_argument(
        "--input-type",
        type=str,
        required=True,
        choices=list(INPUT_FILE_TYPES.keys()),
        help="Input file format.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="The directory for storing output files.",
    )
    parser.add_argument(
        "--period-type",
        type=str,
        required=True,
        choices=list(PERIOD_TYPES.keys()),
        help="Time periods",
    )
    args = parser.parse_args()

    try:
        filter_articles(
            input_dir=args.input_dir,
            glob_pattern=args.glob,
            config_path=args.config_path,
            input_type=args.input_type,
            output_dir=args.output_dir / "output_filter",
        )
        categorize_articles(
            input_dir=args.output_dir / "output_filter",
            period_type=args.period_type,
            glob_pattern="*.json",
            output_dir=args.output_dir / "output_timestamped",
        )

        select_final_articles(
            input_dir=args.output_dir / "output_timestamped",
            glob_pattern="*.csv",
            config_path=args.config_path,
        )

        generate_output(
                    input_dir=args.output_dir / "output_timestamped",
                    glob_pattern="*.csv",
                    config_path=args.config_path,
                    output_dir=args.output_dir / "results"
        )

    except ValueError as e:
        parser.error(str(e))
    except Exception as e:  # pylint: disable=broad-except
        logging.error("Error occurred in CLI: %s", str(e))


if __name__ == "__main__":
    cli()
