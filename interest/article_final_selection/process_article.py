""" Module for processing articles from gzip files."""
import gzip
import json
import logging
from typing import List, Union, Tuple
from interest.preprocessor.text_cleaner import TextCleaner

text_cleaner = TextCleaner()


def clean(text: str) -> str:
    """
    Clean the input text using TextCleaner.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text.
    """
    return text_cleaner.preprocess(text)

# pylint: disable=too-few-public-methods


class ArticleProcessor:
    """
        Process individual articles from gzip files.

        This class handles the processing of individual articles from
        gzip files.
        It reads the content of the article, cleans it using TextCleaner, and
        determines whether the article contains any keywords of interests in
        the title.
    """
    def __init__(self, gzip_file_path: str, article_id: int):
        """
        Initialize ArticleProcessor with the gzip file path and article ID.

        Args:
            gzip_file_path (str): The path to the gzip file.
            article_id (int): The ID of the article.
        """
        self._file_path = gzip_file_path
        self._article_id = article_id
        self._title: Union[str, None] = ''
        self._body: Union[str, None] = ''
        self.selected: bool = False

    def _read_article_from_gzip(self) -> Tuple[Union[str, None],
                                               Union[str, None]]:
        """
        Read article content from a gzip file.

        Returns:
            Tuple[Union[str, None], Union[str, None]]: A tuple containing
            the title and body of the article.
        """
        try:
            with gzip.open(self._file_path, 'rt') as f:
                data = json.load(f)
                articles = data.get('articles', {})
                article = articles.get(str(self._article_id), {})
                title = article.get('title', {})
                body = article.get('body', {})
                body_string = " ".join(body)
                return title, body_string
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Error reading article %s from %s: %s",
                          str(self._article_id), self._file_path, e)
            return None, None

    def process_article(self, clean_keywords: List[str]) -> str:
        """
        Process the article content.

        Args:
            clean_keywords (List[str]): A list of clean keywords.

        Returns:
            str: The processed article body.
        """
        self._title, self._body = self._read_article_from_gzip()
        if (self._title is None) or (self._body is None):
            return ""
        clean_title = clean(self._title)
        title_with_keyword = any(keyword in clean_title
                                 for keyword in clean_keywords)
        if title_with_keyword:
            self.selected = True
            return ""
        return clean(self._body)
