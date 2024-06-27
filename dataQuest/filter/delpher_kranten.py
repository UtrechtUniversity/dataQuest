"""
Delpher Kranten Module

This module provides classes and functions for handling Delpher Kranten files.
"""

import json
import logging
import os
from typing import Optional
from dataQuest.filter.document import Document, Article
from dataQuest.filter.input_file import InputFile


class KrantenFile(InputFile):
    """
    An InputFile implementation for Delpher Kranten.

    Input is a zip file which includes one JSON file. The JSON file contains
    metadata and articles from one issue of a newspaper.

    Attributes:
        METADATA_FIELD (str): The key for metadata field in JSON data.
        TITLE_FIELD (str): The key for title field in metadata.
        DATE_FIELD (str): The key for date field in metadata.
        LANGUAGE_FIELD (str): The key for language field in metadata.
        ARTICLES_FIELD (str): The key for articles field in JSON data.
        ARTICLE_TITLE_FIELD (str): The key for title field in an article.
        ARTICLE_BODY_FIELD (str): The key for body field in an article.
        ENCODING (str): The encoding format for reading the file.

    Methods:
        read_json(json_file): Read JSON data from a file and parse it into
        a Document object.
        base_file_name(): Extract the base file name without extension from
        the filepath.
        doc(): Read the directory and parse the JSON file into a Document
        object.
    """

    METADATA_FIELD = "newsletter_metadata"
    TITLE_FIELD = "title"
    DATE_FIELD = "date"
    LANGUAGE_FIELD = "language"
    ARTICLES_FIELD = "articles"
    ARTICLE_TITLE_FIELD = "title"
    ARTICLE_BODY_FIELD = "body"
    ENCODING = "utf-8"

    def read_json(self, json_file) -> Optional[Document]:
        """
                Read JSON data from a file and parse it into a Document object.

                Args:
                    json_file: A file object containing JSON data.

                Returns:
                    Optional[Document]: A Document object parsed from
                    the JSON data, or None if parsing fails.
        """
        try:
            json_data = json.load(json_file)
            metadata = json_data[self.METADATA_FIELD]
            document_title = metadata[self.TITLE_FIELD]
            publish_date = metadata[self.DATE_FIELD]
            language = metadata[self.LANGUAGE_FIELD]

            articles_data = json_data[self.ARTICLES_FIELD]

            articles = []
            for article_id, article in articles_data.items():
                article_title = article[self.ARTICLE_TITLE_FIELD]
                article_body = article[self.ARTICLE_BODY_FIELD]
                article = Article(article_id=article_id, title=article_title,
                                  body=article_body)
                articles.append(article)

            document = Document(title=document_title,
                                publish_date=publish_date,
                                language=language,
                                articles=articles)
            return document

        except (json.JSONDecodeError, KeyError) as e:
            logging.error("Error parsing JSON data: %s", e)
            return None

    def base_file_name(self) -> str:
        """
               Extract the base file name without extension from the filepath.

               Returns:
                   str: The base file name without extension.
        """
        file_name_json = os.path.splitext(os.path.basename(self.filepath))[0]
        base_file_name = os.path.splitext(file_name_json)[0]
        return base_file_name

    def doc(self) -> Optional[Document]:
        """
                Read the directory and parse the JSON file into a Document
                object.

                Returns:
                    Optional[Document]: A Document object parsed from the
                    JSON data, or None if parsing fails.
        """
        try:
            logging.info("Reading directory '%s'...", self._filepath)
            fh = self.open(encoding=self.ENCODING)
            document = self.read_json(fh)
            fh.close()
            return document

        except OSError as e:
            logging.error("Error processing gzip file '%s': %s",
                          self._filepath, e)
            return None
