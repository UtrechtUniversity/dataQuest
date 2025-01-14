"""This script reads selected articles from CSV files,
and saves their text for manual labeling"""
import logging
from pathlib import Path
from typing import Union
import pandas as pd
from pandas import DataFrame
from spacy.language import Language
from dataQuest.settings import SPACY_MODEL
from dataQuest.article_final_selection.process_article import ArticleProcessor
from dataQuest.utils import read_config, get_file_name_without_extension
from dataQuest.output_generator.text_formater import (TextFormatter,
                                                      SEGMENTED_TEXT_FORMATTER)


FILE_PATH_FIELD = "file_path"
TITLE_FIELD = "title"
ARTICLE_ID_FIELD = "article_id"
BODY_FIELD = "body"
LABEL_FIELD = "label"
SELECTED_FIELD = "selected"
DATE_FIELD = "date"

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
    title, body, date = article_processor.read_article_from_gzip()

    body_formatted = formatter.format_output(body)

    dates = [date] * len(body_formatted) \
        if ((not formatter.is_fulltext) and body_formatted is not None) \
        else [date]
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
                         DATE_FIELD: dates,
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


def generate_output(
    input_dir: Path,
    glob_pattern: str,
    config_path: Path,
    output_dir: Path,
    spacy_model: Union[str, Language] = SPACY_MODEL,
):
    """
    Core functionality to select final articles and save them to output files.

    Args:
        input_dir (Path): Directory containing input files.
        glob_pattern (str): Glob pattern to find input files (e.g., '*.csv').
        config_path (Path): Path to the configuration file.
        output_dir (Path): Directory to save output files.
        spacy_model (Union[str, Language]): SpaCy model to use for text processing.
    """
    if not input_dir.is_dir():
        raise ValueError(f"Not a directory: '{str(input_dir.absolute())}'")

    output_dir.mkdir(parents=True, exist_ok=True)

    output_unit = read_config(config_path, OUTPUT_UNIT_KEY)
    sentences_per_segment = '0'

    if output_unit == SEGMENTED_TEXT_FORMATTER:
        sentences_per_segment = str(read_config(config_path, SENTENCE_PER_SEGMENT_KEY))

    text_formatter = TextFormatter(
        str(output_unit),
        int(sentences_per_segment),
        spacy_model=spacy_model,
    )

    for articles_filepath in input_dir.rglob(glob_pattern):
        try:
            df = find_articles_in_file(str(articles_filepath), text_formatter)
            if df is None:
                continue

            file_name = get_file_name_without_extension(str(articles_filepath))
            output_file = output_dir / f"to_label_{file_name}.csv"
            df.to_csv(output_file, index=False)
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error processing file %s: %s", articles_filepath, str(e))
