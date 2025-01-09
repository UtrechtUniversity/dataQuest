"""
This script filter articles from input files according to
specified configurations.
"""

import argparse
from pathlib import Path
from typing import Iterable
from tqdm import tqdm
from dataQuest.filter import INPUT_FILE_TYPES
from dataQuest.filter.input_file import InputFile
from dataQuest.utils import load_filters_from_config
from dataQuest.utils import save_filtered_articles


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

    args = parser.parse_args()

    try:
        filter_articles(
            input_dir=args.input_dir,
            glob_pattern=args.glob,
            config_path=args.config_path,
            input_type=args.input_type,
            output_dir=args.output_dir,
        )
    except ValueError as e:
        parser.error(str(e))


if __name__ == "__main__":
    cli()
