# pylint: disable=too-few-public-methods
"""
This module defines the Document class, which represents a document
containing articles.
"""
import logging
from typing import Optional, List, Union
from datetime import datetime


class Article:
    """A class representing an article.

        This class represents an article with an ID, title, and body text.
        The body text can be provided as a list
        of paragraphs, which will be joined into a single string.

        Attributes:
            id (str): The unique identifier of the article.
            title (str): The title of the article.
            body (str): The body text of the article, represented as
            a single string.
    """
    def __init__(self, article_id: str, title: str,
                 body: Union[str, List[str]]) -> None:
        """Initialize an Article object with the given ID, title, and body.

                Args:
                    id (str): The unique identifier of the article.
                    title (str): The title of the article.
                    body (Union[str, List[str]): The body text of the article,
                    provided as a list of paragraphs.
        """
        self.id = article_id
        self.title = title
        if isinstance(body, list):
            if any(item is None for item in body):
                logging.warning("There is a None value in body")
                self.text = ""
            else:
                article_body = '\n'.join(body)
                self.text = article_body
        else:
            self.text = body


class Document:
    """
        Represents a document containing articles.

        Args:
            title (str): The title of the document.
            publish_date (str): The publication date of the document in
            the format 'YYYY-MM-DD'.
            language (str): The language of the document.
            articles (List[Article]): A list of articles included in
             the document.

        Attributes:
            _title (str): The title of the document.
            _publish_date (str): The publication date of the document in
            the format 'YYYY-MM-DD'.
            _year (Optional[int]): The year of publication, extracted from
            publish_date.
            _language (str): The language of the document.
            _articles (List[Article]): A list of articles included in the
             document.

        Properties:
            title (str): Getter for the title of the document.
            publish_date (str): Getter for the publication date of the
            document.
            year (Optional[int]): Getter for the year of publication.
            decade (Optional[int]): Getter for the decade of publication.
            language (str): Getter for the language of the document.
            articles (List[Article]): Getter for the list of articles
            included in the document.
    """
    def __init__(self, title: str, publish_date: str, language: str,
                 articles: List[Article]) -> None:
        self._year: Optional[int] = None
        self._articles = articles
        self._title = title
        self._publish_date = publish_date
        self._language = language

    @property
    def title(self) -> str:
        """
            Getter for the title of the document.

            Returns:
                str: The title of the document.
        """
        return self._title

    @property
    def publish_date(self) -> str:
        """
           Getter for the publish_date of the document.

           Returns:
               str: The publish_date of the document.
        """
        return self._publish_date

    @property
    def year(self) -> Optional[int]:
        """
            Getter for the year of publication.

            Returns:
                Optional[int]: The year of publication extracted
                from publish_date, or None if it cannot be determined.
        """
        if self._year is not None:
            return self._year
        try:
            date_obj = datetime.strptime(self._publish_date, '%Y-%m-%d')
            self._year = date_obj.year
            return self._year
        except ValueError:
            return None

    @property
    def decade(self) -> Optional[int]:
        """
            Getter for the decade of publication.

            Returns:
                Optional[int]: The decade of publication extracted from
                publish_date,
                or None if it cannot be determined.
        """
        _ = self.year
        return int(self._year / 10) * 10 if self._year is not None else None

    @property
    def articles(self) -> List[Article]:
        """
            Getter for the list of articles included in the document.

            Returns:
                List[Article]: The list of articles included in the document.
        """
        return self._articles
