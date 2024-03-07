"""
Document Filter Module
This module provides classes for filtering documents and articles.
"""
from abc import ABC, abstractmethod
from typing import List
from .document import Document, Article


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
       Filter documents by year.

       Attributes:
           year (int): The year to filter by.
    """
    def __init__(self, year: int):
        self.year = year

    def filter_document(self, document: Document) -> bool:
        """
                Filter documents by year.

                Args:
                    document (Document): The document to be filtered.

                Returns:
                    bool: True if the document's year matches the specified
                    year, False otherwise.
        """
        return document.year == self.year


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


class CompoundFilter(DocumentFilter):
    """
        Compound filter combining multiple filters.

        Attributes:
            filters (List[DocumentFilter]): The list of filters to apply.
    """
    def __init__(self, filters: List[DocumentFilter]):
        self.filters = filters

    def filter_document(self, document: Document) -> bool:
        """
                Filter documents by applying all filters.

                Args:
                    document (Document): The document to be filtered.

                Returns:
                    bool: True if the document passes all filters,
                    False otherwise.
        """
        return all(filter_.filter_document(document)
                   for filter_ in self.filters)

    def filter_article(self, article: Article) -> bool:
        """
                Filter articles by applying all filters.

                Args:
                    article (Article): The article to be filtered.

                Returns:
                    bool: True if the article passes all filters,
                    False otherwise.
        """
        return all(filter_.filter_article(article) for filter_ in self.filters)

    def include_keyword_filter(self) -> bool:
        """
                Check if the compound filter includes a KeywordsFilter.

                Returns:
                    bool: True if the compound filter includes a
                    KeywordsFilter, False otherwise.
        """
        for filter_ in self.filters:
            if isinstance(filter_, KeywordsFilter):
                return True
        return False
