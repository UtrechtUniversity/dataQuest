"""Base class for document embeddings."""

from abc import ABC, abstractmethod
from typing import Union, Sequence, Dict, Any

#from docembedder.typing import AllEmbedType


class BaseEmbedder(ABC):
    """Base class for creating document embeddings."""

    @abstractmethod
    def fit(self, documents: Sequence[str]) -> None:
        """Train the model on documents."""

    @abstractmethod
    def transform(self, documents: Union[str, Sequence[str]]): #-> AllEmbedType:
        """Get the embedding for a document."""
