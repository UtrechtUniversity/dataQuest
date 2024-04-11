"""This script reads selected articles from CSV files,
and saves their text for manual labeling"""
import argparse
import logging
import os
from pathlib import Path
from typing import Union
import pandas as pd
from pandas import DataFrame
from interest.settings import SPACY_MODEL
from interest.article_final_selection.process_article import ArticleProcessor
from interest.utils import read_config
from interest.output_generator.text_formater import (TextFormatter,
                                                     SEGMENTED_TEXT_FORMATTER)


FILE_PATH_FIELD = "file_path"
ARTICLE_ID_FIELD = "article_id"
TITLE_FIELD = "title"
BODY_FIELD = "body"
LABEL_FIELD = "label"
SELECTED_FIELD = "selected"

OUTPUT_UNIT_KEY = "output_unit"
SENTENCE_PER_SEGMENT_KEY = "sentences_per_segment"


def read_article(row: pd.Series, formatter: TextFormatter) -> DataFrame:
    """
    Read article from row and return DataFrame of articles.

    Args:
        row (pd.Series): A row from a DataFrame.
        formatter (TextFormatter): An object of TextFormatter to format
        output text. Defaults to False.

    Returns:
        DataFrame: DataFrame containing article information.
    """
    file_path = row[FILE_PATH_FIELD]
    article_id = row[ARTICLE_ID_FIELD]
    article_processor = ArticleProcessor(file_path, article_id)
    title, body = article_processor.read_article_from_gzip()

    body_formatted = formatter.format_output(body)

    titles = [title] * len(body_formatted) \
        if ((not formatter.is_fulltext) and body_formatted is not None) \
        else [title]
    files_path = [file_path] * len(body_formatted) \
        if ((not formatter.is_fulltext) and body_formatted is not None) \
        else [file_path]
    articles_id = ([article_id] * len(body_formatted)) \
        if (not formatter.is_fulltext) and body_formatted is not None \
        else [article_id]
    label = [''] * len(body_formatted) \
        if (not formatter.is_fulltext) and body_formatted is not None \
        else ['']
    return pd.DataFrame({FILE_PATH_FIELD: files_path,
                         ARTICLE_ID_FIELD: articles_id,
                         TITLE_FIELD: titles,
                         BODY_FIELD: body_formatted,
                         LABEL_FIELD: label})


def find_articles_in_file(filepath: str, formatter: TextFormatter) -> (
        Union)[DataFrame, None]:
    """
    Find selected articles in a CSV file and return DataFrame of articles.

    Args:
        filepath (str): Path to the CSV file.
        formatter (TextFormatter): An object of TextFormatter to format
        output text.

    Returns:
        DataFrame: DataFrame containing selected articles information.
    """
    try:
        df_articles = pd.read_csv(filepath)
        df_selected = df_articles.loc[df_articles[SELECTED_FIELD] == 1]

        result = pd.concat([read_article(row, formatter)
                            for _, row in df_selected.iterrows()],
                           axis=0, ignore_index=True)
        return result
    except Exception as e:  # pylint: disable=W0718
        logging.error("Error reading selected indices in file: %s", e)
        return None


if __name__ == "__main__":
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
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="The directory for storing output files.",
    )

    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"Not a directory: '{str(args.input_dir.absolute())}'")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_unit = read_config(args.config_path, OUTPUT_UNIT_KEY)

    SENTENCES_PER_SEGMENT = '0'
    if output_unit == SEGMENTED_TEXT_FORMATTER:
        SENTENCES_PER_SEGMENT = str(read_config(args.config_path,
                                                SENTENCE_PER_SEGMENT_KEY))

    result_df = pd.DataFrame(columns=[FILE_PATH_FIELD, ARTICLE_ID_FIELD,
                                      TITLE_FIELD, BODY_FIELD, LABEL_FIELD])

    text_formatter = TextFormatter(str(output_unit),
                                   int(SENTENCES_PER_SEGMENT),
                                   spacy_model=SPACY_MODEL)
    for articles_filepath in args.input_dir.rglob(args.glob):
        df = find_articles_in_file(articles_filepath, text_formatter)
        result_df = pd.concat([result_df, df], ignore_index=True)

    result_df.to_csv(os.path.join(args.output_dir, 'articles_to_label.csv'))
