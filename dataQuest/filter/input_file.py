"""
Input File Module
This module provides an abstract class for representing various input files.
"""

import abc
import gzip
import logging
from pathlib import Path
from typing import Iterable, TextIO, cast, Optional
from dataQuest.filter.document import Document, Article
from dataQuest.filter.document_filter import DocumentFilter


class InputFile(abc.ABC):
    """
    Abstract class for representing various input files.

    Attributes:
        _filepath (Path): The file path of the input file.

    Methods:
        __init__(filepath): Initialize the InputFile with a file path.
        filepath(): Get the file path of the input file.
        base_file_name(): Output a list of documents in the input file.
        open(mode, encoding): Open the input file for reading.
        articles(): Return all articles for the document found in the
        input file.
        doc(): Output a list of documents in the input file.
    """

    def __init__(self, filepath: Path) -> None:
        """
               Initialize the InputFile with a file path.

               Args:
                   filepath (Path): The file path of the input file.
        """
        self._filepath = filepath

    @property
    def filepath(self) -> Path:
        """
                Get the file path of the input file.

                Returns:
                    Path: The file path of the input file.
        """
        return self._filepath

    @abc.abstractmethod
    def base_file_name(self) -> str:
        """
        Output a list of documents in the input file.

        This can be a singleton list if an input file contains only
        one document.

        Returns:
            str: The base file name without extension.
        """
        return NotImplemented

    def open(self, mode: str = "rt", encoding=None) -> TextIO:
        """
                Open the input file for reading.

                Args:
                    mode (str): The file open mode.
                    encoding: The encoding format.

                Returns:
                    TextIO: A file object for reading the input file.
        """
        if self._filepath.suffix.startswith(".gz"):
            return cast(TextIO, gzip.open(self._filepath, mode=mode,
                                          encoding=encoding))

        # Default to text file
        return cast(TextIO, open(self._filepath,
                                 mode=mode, encoding=encoding))

    # pylint: disable=no-member
    def articles(self) -> Iterable[Article]:
        """
        Return all articles for the document found in the input file.

        Yields:
            Article: An article object.
        """
        doc = self.doc()
        if doc is not None:
            yield from doc.articles
        else:
            logging.error("Document not found or is None for filepath: %s",
                          self.filepath)
            return

    @abc.abstractmethod
    def doc(self) -> Optional[Document]:
        """
            Output a list of documents in the input file.

            This can be a singleton list if an input file contains only
            one document.

            Returns:
                Document: A document object.
        """
        return NotImplemented

    def selected_articles(self, filter: DocumentFilter) -> Iterable[Article]:
        document = self.doc()
        if document is not None:
            if filter.filter_document(document):
                if document.articles is not None:
                    for article in document.articles:
                        if filter.filter_article(article):
                            yield article
