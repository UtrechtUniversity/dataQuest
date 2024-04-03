"""This script reads selected articles from CSV files,
and saves their text for manual labeling"""
import argparse
import logging
import os
from pathlib import Path
from typing import Union
import pandas as pd
from pandas import DataFrame
from interest.article_final_selection.process_article import ArticleProcessor
from interest.utils import get_output_unit_from_config

FILE_PATH_FIELD = "file_path"
ARTICLE_ID_FIELD = "article_id"
TITLE_FIELD = "title"
BODY_FIELD = "body"
LABEL_FIELD = "label"
SELECTED_FIELD = "selected"


def read_article(row: pd.Series, in_paragraph: bool = False) -> DataFrame:
    """
    Read article from row and return DataFrame of articles.

    Args:
        row (pd.Series): A row from a DataFrame.
        in_paragraph (bool, optional): Whether to read article in paragraphs.
        Defaults to False.

    Returns:
        DataFrame: DataFrame containing article information.
    """
    file_path = row[FILE_PATH_FIELD]
    article_id = row[ARTICLE_ID_FIELD]
    article_processor = ArticleProcessor(file_path, article_id)
    title, body = article_processor.read_article_from_gzip(in_paragraph)

    titles = [title] * len(body) if in_paragraph and body is not None else [title]
    files_path = [file_path] * len(body) if in_paragraph and body is not None else [file_path]
    articles_id = [article_id] * len(body) if in_paragraph and body is not None else [article_id]
    label = [''] * len(body) if in_paragraph and body is not None else ['']
    return pd.DataFrame({FILE_PATH_FIELD: files_path,
                         ARTICLE_ID_FIELD: articles_id,
                         TITLE_FIELD: titles,
                         BODY_FIELD: body,
                         LABEL_FIELD: label})


def find_articles_in_file(filepath: str, in_paragraph: bool) -> (
        Union)[DataFrame, None]:
    """
    Find selected articles in a CSV file and return DataFrame of articles.

    Args:
        filepath (str): Path to the CSV file.
        in_paragraph (bool): Whether to read articles in paragraphs.

    Returns:
        DataFrame: DataFrame containing selected articles information.
    """
    try:
        df_articles = pd.read_csv(filepath)
        df_selected = df_articles.loc[df_articles[SELECTED_FIELD] == 1]

        result = pd.concat([read_article(row, in_paragraph=in_paragraph)
                            for _, row in df_selected.iterrows()],
                           axis=0, ignore_index=True)
        return result
    except Exception as e:  # pylint: disable=W0718
        logging.error("Error reading selected indices in file: %s", e)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Select final articles.")

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
    config_output_unit = get_output_unit_from_config(args.config_path)

    result_df = pd.DataFrame(columns=[FILE_PATH_FIELD, ARTICLE_ID_FIELD,
                                      TITLE_FIELD, BODY_FIELD, LABEL_FIELD])
    IN_PARAGRAPH = config_output_unit == "paragraph"

    for articles_filepath in args.input_dir.rglob(args.glob):
        df = find_articles_in_file(articles_filepath,
                                   in_paragraph=IN_PARAGRAPH)
        result_df = pd.concat([result_df, df], ignore_index=True)

    result_df.to_csv(os.path.join(args.output_dir, 'articles_to_label.csv'))
