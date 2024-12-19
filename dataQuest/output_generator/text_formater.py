""" This module defines a TextFormatter class for formatting text based on
specified output units. """
from typing import List, Union
import logging
from spacy.language import Language
from dataQuest.utils import initialize_nlp

PARAGRAPH_FORMATTER = 'paragraph'
FULLTEXT_FORMATTER = 'full_text'
SEGMENTED_TEXT_FORMATTER = 'segmented_text'


class TextFormatter:
    # pylint: disable=R0903
    """Class for formatting text based on specified output units. """

    def __init__(self, output_unit: str, sentences_per_segment: int,
                 spacy_model: Union[str, Language]) -> None:
        """
            Initializes the TextFormatter object.

            Args:
                output_unit (str): The type of output unit ('paragraph',
                 'full_text', 'segmented_text').
                sentences_per_segment (int): Number of sentences per
                segment when output_unit is 'segmented_text'.
                spacy_model (Union[str, Language], optional): Spacy model
                 or model name used for text processing. Defaults to the global
                 SPACY_MODEL value.
        """
        self.nlp: Language = initialize_nlp(spacy_model)
        if not callable(self.nlp):
            raise ValueError("Failed to initialize SpaCy NLP pipeline.")

        self.sentences_per_segment = sentences_per_segment
        self.formatter = output_unit
        self.is_fulltext = self._is_fulltext()
        self.texts: List[str] = []

    def format_output(self, texts: Union[None, List[str]]) -> (
            Union)[str, List[str], List[List[str]], None]:
        """
        Formats input texts based on the specified output unit.

        Args:
            texts (List[str]): List of input texts to be formatted.

        Returns:
            Union[str, List[str], List[List[str]]]: Formatted output text
            based on the selected output_unit. For 'full_text', returns a
            single string. For 'paragraph' and 'segmented_text', returns a
            list of segmented text lists.

        Raises:
            ValueError: If input 'texts' is not a list of strings.
            ValueError: If an unsupported formatter type is specified.
        """
        try:
            if (not isinstance(texts, list) or (texts is None) or
                    not all(isinstance(text, str) for text in texts)):
                raise ValueError("Input 'texts' must be a list of strings.")

            self.texts = texts

            if self.formatter == PARAGRAPH_FORMATTER:
                return self._format_paragraph()
            if self.formatter == FULLTEXT_FORMATTER:
                return self._format_fulltext()
            if self.formatter == SEGMENTED_TEXT_FORMATTER:
                return self._format_segmented_text()

        except ValueError as e:
            logging.error("Unsupported formatter %s: %s", self.formatter, e)
            return None
        return None

    def _format_paragraph(self) -> List[str]:
        """Formats texts as a single paragraph.

        Returns:
            List[List[str]]: List of input texts, segmented in paragraphs.
        """
        return self.texts

    def _format_fulltext(self) -> str:
        """Formats texts as full text with newline separators.

        Returns:
            str: Newline-separated string of input texts.
        """
        return '\n'.join(self.texts)

    def _format_segmented_text(self) -> List[List[str]]:
        """Formats texts as segmented text based on sentences_per_segment.

        Returns:
             List[List[str]]: Flattened list of segmented text strings.
        """
        if not callable(self.nlp):
            raise ValueError("SpaCy NLP pipeline (self.nlp) is not initialized or invalid.")

        segmented_texts = []
        for text in self.texts:
            doc = self.nlp(text)
            sentences = [sent.text for sent in doc.sents]

            for i in range(0, len(sentences), self.sentences_per_segment):
                segment = sentences[i:i + self.sentences_per_segment]
                segmented_texts.append(segment)

        return segmented_texts

    def _is_fulltext(self) -> bool:
        """Checks if the formatter type is 'full_text'.

        Returns:
            bool: True if formatter is 'full_text', False otherwise.
        """
        return self.formatter == FULLTEXT_FORMATTER
