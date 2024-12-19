"""
This module provides a TextCleaner class for preprocessing text
data using various cleaning techniques.
"""
import re
from typing import Union, List
from spacy.language import Language
from dataQuest.settings import SPACY_MODEL
from dataQuest.utils import initialize_nlp


def merge_texts_list(text: Union[str, List[str]]) -> str:
    """
    Merge a list of texts into a single string by joining them with spaces.

    Args:
        text (Union[str, List[str]]): The input text or list of texts to merge.

    Returns:
        str: The merged text if input is a list of strings, otherwise returns
        the input text unchanged.
    """
    if isinstance(text, list):
        merged_text = ' '.join(text)
        return merged_text
    return text


class TextCleaner:
    """A class for cleaning text data using various preprocessing
       techniques."""

    def __init__(self, spacy_model: Union[str, Language] = SPACY_MODEL) -> None:
        """Initialize the TextCleaner instance.

        Args:
            spacy_model (str or spacy.Language, optional): The SpaCy
                        model to use for text processing.
                        Defaults to the model specified in the settings.
        """
        self.nlp: Language = initialize_nlp(spacy_model)
        self.stopword_list = self.nlp.Defaults.stop_words
        self.stopwords = set(self.stopword_list)
        self.text = ""

    def get_lower_lemma_tokens(self) -> None:
        """
            Get lowercased lemmatized tokens from the text.

            This method processes the text stored in the instance variable
            `self.text`,tokenizes it using the SpaCy pipeline `self.nlp`,
            and then lemmatizes each token, converting it to lowercase.
            Stop words and punctuation tokens are filtered out.
        """
        doc = self.nlp(self.text)
        self.text = " ".join([token.lemma_.lower() for token in doc
                              if not token.is_stop and not token.is_punct])

    def get_words(self):
        """Tokenize words in the text."""
        doc = self.nlp(self.text)
        self.text = " ".join([token.text for token in doc])

    def lower(self):
        """Transform the text to lower case."""
        self.text = self.text.lower()

    def remove_stopwords(self):
        """Remove the stopwords from the text."""
        doc = self.nlp(self.text)
        self.text = " ".join([token.text for token in doc if token.text
                              not in self.stopwords])

    def remove_numeric(self):
        """Remove numbers from the text."""
        self.text = re.sub(r'\d+', '', self.text)

    def remove_non_ascii(self):
        """Remove non ASCII characters from the text."""
        self.text = re.sub(r'[^\x00-\x7f]', '', self.text)

    def remove_extra_whitespace_tabs(self):
        """Remove extra whitespaces and tabs from the text."""
        self.text = re.sub(r'\s+', ' ', self.text)

    def remove_one_char(self):
        """Remove single characters from the text."""
        self.text = " ".join([w for w in self.text.split() if len(w) > 1])

    def keep_standard_chars(self):
        """Keep only standard characters in the text."""
        self.text = re.sub(r'[^-0-9\w,. ?!()%/]', '', self.text)

    def preprocess(self, text):
        """Preprocess the given text using a series of cleaning steps.

        Args:
            text ( List[str]): The text to preprocess.

        Returns:
            str: The preprocessed text.
        """
        self.text = merge_texts_list(text)
        self.get_lower_lemma_tokens()
        self.remove_numeric()
        self.remove_extra_whitespace_tabs()
        self.remove_one_char()
        return self.text

    def clean(self, text):
        """Clean the given text by removing non-standard characters and
           extra whitespace.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        self.text = merge_texts_list(text)
        self.text = text
        self.get_words()
        self.keep_standard_chars()
        self.remove_extra_whitespace_tabs()
        return self.text
