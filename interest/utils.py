"""
Module containing utility functions for the project.
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import json
from sklearn.feature_extraction.text import CountVectorizer  # type: ignore
from interest.document_filter import YearFilter, TitleFilter, DocumentFilter
from interest.document_filter import (CompoundFilter, DecadeFilter,
                                      KeywordsFilter)
from interest.settings import ENCODING


def calculate_word_frequency_per_doc(document: str) -> Dict[str, int]:
    """Calculate the word frequency per document.

    Args:
        document (str): The document for which word frequency is to be
        calculated.

    Returns:
        dict: A dictionary where keys are words and values are their respective
         frequencies.
    """
    vectorizer = CountVectorizer()
    word_frequency_matrix = vectorizer.fit_transform([document])
    vocabulary = vectorizer.get_feature_names_out()
    word_frequency_vector = word_frequency_matrix.toarray()[0]
    word_frequency_dict = dict(zip(vocabulary, word_frequency_vector.tolist()))

    return word_frequency_dict


def load_filters_from_config(config_file: Path) -> CompoundFilter:
    """Load document filters from a configuration file.

    Args:
        config_file (Path): Path to the configuration file containing
        filter settings.

    Returns:
        CompoundFilter: A compound filter containing individual document
        filters loaded from the configuration.
    """
    with open(config_file, 'r', encoding=ENCODING) as f:
        config: Dict[str, List[Dict[str, Any]]] = json.load(f)

    filters: List[DocumentFilter] = []
    for filter_config in config['filters']:
        filter_type = filter_config['type']
        if filter_type == 'TitleFilter':
            filters.append(TitleFilter(filter_config['title']))
        elif filter_type == 'YearFilter':
            filters.append(YearFilter(filter_config['year']))
        elif filter_type == 'DecadeFilter':
            filters.append(DecadeFilter(filter_config['decade']))
        elif filter_type == 'KeywordsFilter':
            filters.append(KeywordsFilter(filter_config['keywords']))

    return CompoundFilter(filters)


def save_filtered_articles(input_file: Any, article_id: str, word_freq: Dict[str, int],
                           output_dir: str) -> None:
    """Save filtered articles data to a JSON file.

    Args:
        input_file: The input file object.
        article_id (str): The ID of the article.
        word_freq (Dict[str, int]): Word frequency data for the article.
        output_dir (str): The directory where the JSON file will be saved.

    Returns:
        None
    """
    data = {
        "file_path": str(input_file.filepath),
        "article_id": str(article_id),
        "Date": str(input_file.doc().publish_date),
        "Title": input_file.doc().title,
        "word_freq": word_freq
    }

    output_fp = os.path.join(output_dir, input_file.base_file_name() + '.json')
    print('output_fp', output_fp)
    with open(output_fp, "w", encoding=ENCODING) as json_file:
        json.dump(data, json_file, indent=4)
