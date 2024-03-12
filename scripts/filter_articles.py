"""
This script filter articles from input files according to
specified configurations.
"""

import argparse
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from interest import INPUT_FILE_TYPES
# from interest import settings
from interest.input_file import InputFile
# from interest.document_filter import CompoundFilter
# from interest.preprocess.text_cleaner import TextCleaner
# from interest.utils import calculate_word_frequency_per_doc
from interest.utils import load_filters_from_config
# from interest.utils import save_filtered_articles

if __name__ == "__main__":
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
        "--config_path",
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
    # parser.add_argument(
    #     "--output-prefix",
    #     type=str,
    #     required=True,
    #     help="The prefix to generate output file names,
    #     e.g. 'nyt' for 'nyt_1910.txt'",
    # )

    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"Not a directory: '{str(args.input_dir.absolute())}'")

    input_file_class = INPUT_FILE_TYPES[args.input_type]
    input_files: Iterable[InputFile] = [
        input_file_class(path) for path in args.input_dir.rglob(args.glob)
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    compound_filter = load_filters_from_config(args.config_path)
    # text_cleaner = TextCleaner()
    # word_freq={}
    # with_keyword_filter = compound_filter.include_keyword_filter()

    for input_file in tqdm(input_files, desc="Filtering articles",
                           unit="file"):
        for article in input_file.selected_articles(compound_filter):
            print(article.title)
            # if with_keyword_filter:
            #     article_text_clean = text_cleaner.preprocess(article.text)
            #     word_freq =
            #     calculate_word_frequency_per_doc(article_text_clean)
            #
            # save_filtered_articles(input_file, article.id, word_freq,
            # args.output_dir)