"""
Module containing utility functions for the project.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from functools import cache
import json
import spacy
import spacy.cli
from dataQuest.filter.document_filter import (YearFilter,
                                              TitleFilter,
                                              DocumentFilter)
from dataQuest.filter.document_filter import (CompoundFilter,
                                              DecadeFilter,
                                              KeywordsFilter)
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
    """
        Extract keywords from a JSON configuration file.

        Args:
            config_file (Path): The path to the JSON configuration file.

        Returns:
            List[str]: The list of keywords extracted from the configuration
            file.

        Raises:
            FileNotFoundError: If the config file is not found or cannot be
            opened.
            KeyError: If the required keys are not found in the configuration
            file.
            TypeError: If the data in the configuration file is not in the
            expected format.
    """
    try:
        with open(config_file, 'r', encoding=ENCODING) as f:
            config: Dict[str, List[Dict[str, Any]]] = json.load(f)

        for filter_config in config['filters']:
            filter_type = filter_config['type']
            if filter_type == 'KeywordsFilter':
                return filter_config['keywords']
        return []
    except FileNotFoundError as exc:
        raise FileNotFoundError("Config file not found") from exc
    except KeyError as exc:
        raise KeyError("Keywords not found in config file") from exc


def read_config(config_file: Path, item_key: str) -> Dict[str, str]:
    """
        Get the value of the given key item from a JSON file.

        Args:
            config_file (Path): The path to the JSON config file.
            item_key (str): Key item defined in config file.
        Returns:
            Dict[str, str]: The article selector configuration.

        Raises:
            KeyError: If the key item is not found in the config file.
            FileNotFoundError: If the config file is not found.
    """
    try:
        with open(config_file, 'r', encoding=ENCODING) as f:
            config: Dict[str, str] = json.load(f)[item_key]
        if not config:
            raise ValueError("Config is empty")
        return config
    except FileNotFoundError as exc:
        raise FileNotFoundError("Config file not found") from exc
    except KeyError as exc:
        raise KeyError("Key item %s not found in config file") from exc


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
