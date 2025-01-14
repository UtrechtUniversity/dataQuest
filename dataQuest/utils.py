"""
Module containing utility functions for the project.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from functools import cache
import json
import spacy
import spacy.cli
from spacy.language import Language
from dataQuest.filter.document_filter import (YearFilter,
                                              TitleFilter,
                                              DocumentFilter)

from dataQuest.filter.document_filter import (AndFilter,
                                              OrFilter,
                                              NotFilter,
                                              DecadeFilter,
                                              KeywordsFilter,
                                              ArticleTitleFilter)
from dataQuest.settings import ENCODING


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
    nlp.add_pipe("sentencizer")
    return nlp


def create_filter(filter_config: Dict[str, Any]) -> DocumentFilter:
    """
    Factory function to create filters based on configuration.

    Args:
        filter_config (Dict[str, Any]): The filter configuration.

    Returns:
        DocumentFilter: The created filter instance.
    """
    filter_type = filter_config.get('type')

    if filter_type == 'TitleFilter':
        return TitleFilter(filter_config['title'])
    if filter_type == 'YearFilter':
        start_year = filter_config['start_year']
        end_year = filter_config['end_year']
        return YearFilter(start_year, end_year)
    if filter_type == 'DecadeFilter':
        return DecadeFilter(filter_config['decade'])
    if filter_type == 'KeywordsFilter':
        return KeywordsFilter(filter_config['keywords'])
    if filter_type == 'ArticleTitleFilter':
        return ArticleTitleFilter(filter_config['article_title'])
    if filter_type == 'AndFilter':
        return AndFilter([create_filter(f) for f in filter_config['filters']])
    if filter_type == 'OrFilter':
        return OrFilter([create_filter(f) for f in filter_config['filters']])
    if filter_type == 'NotFilter':
        inner_filter = create_filter(filter_config['filter'])
        level = filter_config.get('level', 'both')
        return NotFilter(inner_filter, level)

    raise ValueError(f"Unknown filter type: {filter_type}")


def load_filters_from_config(config_file: Path) -> AndFilter:
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

    filters = [create_filter(filter_config) for filter_config in config['filters']]
    compound_filter = AndFilter(filters)
    return compound_filter


def get_keywords_from_config(config_file: Path) -> List[str]:
    """
    Extract keywords from a JSON configuration file.

    Args:
        config_file (Path): The path to the JSON configuration file.

    Returns:
        List[str]: The list of keywords extracted from the configuration file.

    Raises:
        FileNotFoundError: If the config file is not found or cannot be opened.
        KeyError: If the required keys are not found in the configuration file.
    """
    def extract_keywords(filters: List[Dict[str, Any]]) -> List[str]:
        """Recursively extract keywords from a list of filters."""
        keywords = []
        for filter_config in filters:
            filter_type = filter_config.get("type")
            if filter_type == "KeywordsFilter":
                keywords.extend(filter_config.get("keywords", []))
            elif filter_type in {"AndFilter", "OrFilter"}:
                keywords.extend(extract_keywords(filter_config.get("filters", [])))
            elif filter_type == "NotFilter":
                inner_filter = filter_config.get("filter")
                if inner_filter:
                    keywords.extend(extract_keywords([inner_filter]))
        return keywords

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config: Dict[str, Any] = json.load(f)
        filters = config.get("filters", [])
        return extract_keywords(filters)
    except FileNotFoundError as exc:
        raise FileNotFoundError("Config file not found") from exc
    except KeyError as exc:
        raise KeyError("Keywords not found in config file") from exc


def read_config(config_file: Path, item_key: str) -> Dict[str, Union[str, float, int]]:
    """
        Get the value of the given key item from a JSON file.

        Args:
            config_file (Path): The path to the JSON config file.
            item_key (str): Key item defined in config file.
        Returns:
            Dict[str, Union[str, float, int]]: The article selector configuration.

        Raises:
            KeyError: If the key item is not found in the config file.
            FileNotFoundError: If the config file is not found.
    """
    try:
        with open(config_file, 'r', encoding=ENCODING) as f:
            config: Dict[str, Union[str, float, int]] = json.load(f)[item_key]
        if not config:
            raise ValueError("Config is empty")
        return config
    except FileNotFoundError as exc:
        raise FileNotFoundError("Config file not found") from exc
    except KeyError as exc:
        raise KeyError("Key item %s not found in config file") from exc


def save_filtered_articles(input_file: Any, article_id: str,
                           output_dir: Path) -> None:
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

    output_fp = os.path.join(output_dir, input_file.base_file_name() + '_' +
                             str(article_id) + '.json')

    print('output_fp', output_fp)
    with open(output_fp, "w", encoding=ENCODING) as json_file:
        json.dump(data, json_file, indent=4)


def get_file_name_without_extension(full_path: str) -> str:
    """
    Extracts the file name without extension from a full path.

    Args:
        full_path (str): The full path of the file.

    Returns:
        str: The file name without extension.

    """
    base_name = os.path.basename(full_path)
    file_name_without_ext = os.path.splitext(base_name)[0]
    return file_name_without_ext


def initialize_nlp(spacy_model: Union[str, Language]) -> Language:
    """Initialize the SpaCy model."""
    if isinstance(spacy_model, str):
        model = load_spacy_model(spacy_model)
        if not isinstance(model, Language):
            raise ValueError(f"Loaded SpaCy model is not a Language instance: {spacy_model}")
        return model
    if isinstance(spacy_model, Language):
        return spacy_model
    raise ValueError("Invalid spacy_model. It must be a string or a SpaCy Language instance.")
