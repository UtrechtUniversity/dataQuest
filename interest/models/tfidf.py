"""Sklearn TF-IDF class."""

from typing import Sequence, Union, Optional, Callable, Dict, Any
import warnings

import scipy
from sklearn.feature_extraction.text import TfidfVectorizer

from interest.models.base import BaseEmbedder
from interest.utils import load_spacy_model
from interest.settings import SPACY_MODEL


class TfidfEmbedder(BaseEmbedder):  # pylint: disable=too-many-instance-attributes
    """Sklearn TF-IDF class.

    Based on:
    https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

    Arguments
    ---------
    ngram_max:
        Maximum n-gram, higher numbers mean bigger embeddings.
    stop_words:
        Remove stop words from a certain langauge.
    stem:
        Whether to stem the words. Has a negative impact on performance.
    norm:
        Which kind of normalization is used: "l1", "l2" or None.
    sublinear_tf:
        Apply sublinear term-frequency scaling.
    min_df:
        Minimum document frequency of word to be included in the embedding.
    max_df:
        Maximum document frequency of word to be included in the embedding.
    """

    def __init__(  # pylint: disable=too-many-arguments
            self, ngram_max: int = 1,
            # stop_words: Optional[str]="english",
            # stem: bool = False,
            norm: Optional[str] = "l1",
            sublinear_tf: bool = False,
            min_df: int = 1,
            max_df: float = 1.0,
            spacy_model=SPACY_MODEL):

        self.nlp = (
            load_spacy_model(spacy_model)
            if isinstance(spacy_model, str)
            else spacy_model
        )
        self.stopword_list = self.nlp.Defaults.stop_words
        self.stop_words = list(self.stopword_list)
        self.ngram_max = ngram_max

        self.norm = norm
        self.sublinear_tf = sublinear_tf
        self.min_df = min_df
        self.max_df = max_df
        if self.norm == "None":
            self.norm = None

        self._model: Optional[TfidfVectorizer] = None

    def fit(self, documents: Sequence[str]) -> None:
        min_df = min(self.min_df, len(documents))
        max_df = max(min_df/len(documents), self.max_df)

        def _tokenizer(text):
            doc = self.nlp(text)
            tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
            return tokens

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self._model = TfidfVectorizer(
                ngram_range=(1, self.ngram_max),
                stop_words=self.stop_words,
                tokenizer=_tokenizer,  # self.stem_tokenizer,
                min_df=min_df,
                norm=self.norm,
                sublinear_tf=self.sublinear_tf,
                max_df=max_df)
            self._model.fit(documents)

    def transform(self, documents: Union[str, Sequence[str]]) -> Union[
            scipy.sparse.spmatrix]:
        if self._model is None:
            raise ValueError("Fit TF-IDF model before transforming data.")
        return self._model.transform(documents).tocsr()
