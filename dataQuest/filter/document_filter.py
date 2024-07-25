"""
Document Filter Module
This module provides classes for filtering documents and articles.
"""
from abc import ABC, abstractmethod
from typing import List
from dataQuest.filter.document import Document, Article


class DocumentFilter(ABC):
    """
        Abstract base class for document filters.

        Methods:
            filter_document(document: Document) -> bool: Abstract method
             to filter documents.
            filter_article(article: Article) -> bool: Method to filter
            articles.
    """
    @abstractmethod
    def filter_document(self, document: Document) -> bool:
        """
               Abstract method to filter documents.

               Args:
                   document (Document): The document to be filtered.

               Returns:
                   bool: True if the document passes the filter,
                   False otherwise.
        """
        return NotImplemented

    def filter_article(self, _article: Article) -> bool:
        """
                Method to filter articles.

                By default, returns True, allowing all articles to
                pass through.

                Args:
                    _article (Article): The article to be filtered.

                Returns:
                    bool: True if the article passes the filter,
                     False otherwise.
        """
        return True


class TitleFilter(DocumentFilter):
    """
        Filter documents by title.

        Attributes:
            title (str): The title to filter by.
    """
    def __init__(self, title: str):
        self.title = title

    def filter_document(self, document: Document) -> bool:
        """
                Filter documents by title.

                Args:
                    document (Document): The document to be filtered.

                Returns:
                    bool: True if the document's title contains the specified
                    title, False otherwise.
        """
        return self.title in document.title


class YearFilter(DocumentFilter):
    """
    Filter documents by a range of years.

    Attributes:
        start_year (int): The start year of the range.
        end_year (int): The end year of the range.
    """
    def __init__(self, start_year: int, end_year: int):
        self.start_year = start_year
        self.end_year = end_year

    def filter_document(self, document: Document) -> bool:
        """
        Filter documents by a range of years.

        Args:
            document (Document): The document to be filtered.

        Returns:
            bool: True if the document's year is within the specified range,
            False otherwise.
        """
        if document.year is None:
            return False
        if self.start_year is not None and document.year < self.start_year:
            return False
        if self.end_year is not None and document.year > self.end_year:
            return False
        return True


class DecadeFilter(DocumentFilter):
    """
        Filter documents by decade.

        Attributes:
            decade (int): The decade to filter by.
    """
    def __init__(self, decade: int):
        self.decade = decade

    def filter_document(self, document: Document) -> bool:
        """
                Filter documents by decade.

                Args:
                    document (Document): The document to be filtered.

                Returns:
                    bool: True if the document's decade matches the
                    specified decade, False otherwise.
        """
        return document.decade == self.decade


class KeywordsFilter(DocumentFilter):
    """
        Filter documents and articles by keywords.

        Attributes:
            keywords (List[str]): The list of keywords to filter by.
    """
    def __init__(self, keywords: List[str]):
        self.keywords = keywords

    def filter_document(self, document: Document) -> bool:
        """
                Filter documents by keywords.

                Args:
                    document (Document): The document to be filtered.

                Returns:
                    bool: Always returns True.
        """
        return True

    def filter_article(self, article: Article) -> bool:
        """
                Filter articles by keywords.

                Args:
                    article (Article): The article to be filtered.

                Returns:
                    bool: True if the article's title or text contains any
                    of the specified keywords, False otherwise.
        """
        return any(keyword in article.title or keyword in article.text for
                   keyword in self.keywords)


class ArticleTitleFilter(DocumentFilter):
    """
        Filter documents and articles by article title.

        Attributes:
            article_title (str): The article title to filter by.
    """
    def __init__(self, article_title: str):
        self.article_title = article_title

    def filter_document(self, document: Document) -> bool:
        """
                Filter documents by article title.

                Args:
                    document (Document): The document to be filtered.

                Returns:
                    bool: Always returns True.
        """
        return True

    def filter_article(self, article: Article) -> bool:
        """
                Filter articles by keywords.

                Args:
                    article (Article): The article to be filtered.

                Returns:
                    bool: True if the article's title or text contains any
                    of the specified keywords, False otherwise.
        """
        return self.article_title in article.title


class AndFilter(DocumentFilter):
    """
    Logical AND filter combining multiple filters.

    Attributes:
        filters (List[DocumentFilter]): The list of filters to apply.
    """
    def __init__(self, filters: List[DocumentFilter]):
        self.filters = filters

    def filter_document(self, document: Document) -> bool:
        return all(filter_.filter_document(document) for filter_ in self.filters)

    def filter_article(self, article: Article) -> bool:
        return all(filter_.filter_article(article) for filter_ in self.filters)


class OrFilter(DocumentFilter):
    """
    Logical OR filter combining multiple filters.

    Attributes:
        filters (List[DocumentFilter]): The list of filters to apply.
    """
    def __init__(self, filters: List[DocumentFilter]):
        self.filters = filters

    def filter_document(self, document: Document) -> bool:
        return any(filter_.filter_document(document) for filter_ in self.filters)

    def filter_article(self, article: Article) -> bool:
        return any(filter_.filter_article(article) for filter_ in self.filters)


class NotFilter(DocumentFilter):
    """
    Logical NOT filter to negate a filter's result.

    Attributes:
        filter (DocumentFilter): The filter to negate.
        level (str): The level at which to apply the filter ('document', 'article', or 'both').
    """
    def __init__(self, _filter: DocumentFilter, level: str = 'both'):
        self.filter = _filter
        self.level = level

    def filter_document(self, document: Document) -> bool:
        if self.level in ('document', 'both'):
            result = not self.filter.filter_document(document)
            return result
        return True

    def filter_article(self, article: Article) -> bool:
        if self.level in ('article', 'both'):
            result = not self.filter.filter_article(article)
            return result
        return True
