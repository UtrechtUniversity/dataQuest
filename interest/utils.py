"""
Module containing utility functions for the project.
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import json
from interest.document_filter import YearFilter, TitleFilter, DocumentFilter
from interest.document_filter import (CompoundFilter, DecadeFilter,
                                      KeywordsFilter)
from interest.settings import ENCODING
from functools import cache
import spacy
import spacy.cli
from typing import Optional
@cache
def load_spacy_model(model_name: str, retry: bool = True) \
        -> Optional[spacy.Language]:
    """Load and store a sentencize-only SpaCy model

    Downloads the model if necessary.

    Args:
        model_name (str): The name of the SpaCy model to load.
        retry (bool, optional): Whether to retry downloading the model
            if loading fails initially. Defaults to True.

    Returns:
        spacy.Language: The SpaCy model object for the given name.
    """

    try:
        nlp = spacy.load(model_name, disable=["tagger", "parser", "ner"])
    except OSError as exc:
        if retry:
            spacy.cli.download(model_name)
            return load_spacy_model(model_name, False)
        raise exc
    return nlp

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


def get_keywords_from_config(config_file: Path) -> List[str]:
    with open(config_file, 'r', encoding=ENCODING) as f:
        config: Dict[str, List[Dict[str, Any]]] = json.load(f)

    for filter_config in config['filters']:
        filter_type = filter_config['type']
        if filter_type == 'KeywordsFilter':
            return filter_config['keywords']
    return []


def get_article_selector_from_config(config_file: Path) -> dict:
    try:
        with open(config_file, 'r', encoding=ENCODING) as f:
            config: Dict[str, str] = json.load(f)["article_selector"]
        if config:
            return config
        else:
            raise ValueError("Config is empty")
    except (KeyError, FileNotFoundError):
        raise ValueError("Article selector not found in config file")


def save_filtered_articles(input_file: Any, article_id: str,
                           output_dir: str) -> None:
    """Save filtered articles data to a JSON file.

    Args:
        input_file: The input file object.
        article_id (str): The ID of the article.
        output_dir (str): The directory where the JSON file will be saved.

    Returns:
        None
    """
    data = {
        "file_path": str(input_file.filepath),
        "article_id": str(article_id),
        "Date": str(input_file.doc().publish_date),
        "Title": input_file.doc().title,
    }

    output_fp = os.path.join(output_dir, input_file.base_file_name() + '.json')
    print('output_fp', output_fp)
    with open(output_fp, "w", encoding=ENCODING) as json_file:
        json.dump(data, json_file, indent=4)
