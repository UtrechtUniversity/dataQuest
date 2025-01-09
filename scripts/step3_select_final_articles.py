"""Select final articles."""
import argparse
import logging
from typing import List
from pathlib import Path
import pandas as pd
from tqdm import tqdm  # type: ignore
from dataQuest.utils import get_keywords_from_config
from dataQuest.utils import read_config
from dataQuest.article_final_selection.process_articles import select_articles

ARTICLE_SELECTOR_FIELD = "article_selector"


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
        Command-line interface for selecting final articles.
    """
    parser = argparse.ArgumentParser("Select final articles.")

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Base directory for reading input files.",
    )
    parser.add_argument(
        "--glob",
        type=str,
        default="*.csv",
        help="Glob pattern for find input files; e.g. '*.csv'.",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        default="config.json",
        help="File path of config file.",
    )

    args = parser.parse_args()

    try:
        select_final_articles(
            input_dir=args.input_dir,
            glob_pattern=args.glob,
            config_path=args.config_path,
        )
    except ValueError as e:
        parser.error(str(e))
    except Exception as e:  # pylint: disable=broad-except
        logging.error("Error occurred in CLI: %s", str(e))


if __name__ == "__main__":
    cli()
