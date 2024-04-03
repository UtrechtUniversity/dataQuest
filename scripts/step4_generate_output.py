"""Select final articles."""
import argparse
import logging
from typing import List
from pathlib import Path
import pandas as pd
from pandas import DataFrame
import os
from interest.article_final_selection.process_article import ArticleProcessor
from interest.utils import get_output_unit_from_config


def read_article(row, in_paragraph=False):
    file_path = row['file_path']
    article_id = row['article_id']
    article_processor = ArticleProcessor(file_path, article_id)
    title, body = article_processor.read_article_from_gzip(in_paragraph)

    titles = [title] * len(body) if in_paragraph else [title]
    files_path = [file_path] * len(body) if in_paragraph else [file_path]
    articles_id = [article_id] * len(body) if in_paragraph else [article_id]
    label = [''] * len(body) if in_paragraph else ['']
    return pd.DataFrame({"file_path":files_path,"article_id":articles_id,
                         "title": titles, "body": body, 'label': label})


def find_articles_in_file(filepath: str, in_paragraph: bool) -> DataFrame:
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
            df = pd.read_csv(filepath)
            df_selected = df.loc[df["selected"] == 1,]

            result = pd.concat([read_article(row, in_paragraph=in_paragraph)
                                for _, row in df_selected.iterrows()],
                               axis=0, ignore_index=True)
            return result
    except Exception as e:  # pylint: disable=W0718
        logging.error("Error reading selected indices in file: %s",
                      e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Save results.")

    parser.add_argument(
        "--input_dir",
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
        "--config_path",
        type=Path,
        default="config.json",
        help="File path of config file.",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=True,
        help="The directory for storing output files.",
    )

    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"Not a directory: '{str(args.input_dir.absolute())}'")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    config_output_unit = get_output_unit_from_config(
        args.config_path)

    result_df = pd.DataFrame(columns=['file_path', 'article_id', 'title', 'body', 'label'])
    in_paragraph = True if config_output_unit == "paragraph" else False
    for articles_filepath in args.input_dir.rglob(args.glob):
        df = find_articles_in_file(articles_filepath, in_paragraph=in_paragraph)
        result_df = pd.concat([result_df,df], ignore_index=True)

    result_df.to_csv(os.path.join(args.output_dir,'articles_to_label.csv'))




