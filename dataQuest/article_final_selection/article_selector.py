"""Module containing the ArticleSelector class for selecting articles based on
similarity scores."""

from typing import List, Dict, Union


class ArticleSelector:
    """Class for selecting articles based on similarity scores and
    configuration parameters."""
    # pylint: disable=too-few-public-methods

    def __init__(self, similarity_scores: List[float],
                 config: Dict[str, Union[str, float, int]]):
        """Initializes the ArticleSelector object.

        Args:
            similarity_scores (List[float]): A list of similarity scores
             between keywords and articles.
            config (Dict[str, Union[str, float, int]]): A dictionary containing
            configuration parameters for selecting articles.
        """
        self.similarity_scores = similarity_scores
        self.config = config

    def select_articles(self) -> List[int]:
        """Selects articles based on the configured selection method and value.

        Returns:
            List[int]: A list of indices of selected articles.
        """
        sorted_indices = sorted(
            range(len(self.similarity_scores)),
            key=lambda i: self.similarity_scores[i],
            reverse=True
        )

        selected_indices: List[int] = []
        if self.config["type"] == "threshold":
            threshold = float(self.config["value"])
            selected_indices.extend(
                i for i, score in enumerate(self.similarity_scores)
                if score >= threshold
            )
        elif self.config["type"] == "num_articles":
            num_articles = int(self.config["value"])
            selected_indices.extend(sorted_indices[:num_articles])

        elif self.config["type"] == "percentage":
            percentage = float(self.config["value"])
            num_articles = int(len(self.similarity_scores) *
                               (percentage / 100.0))
            num_articles = len(self.similarity_scores) if num_articles == 0\
                else num_articles
            selected_indices.extend(sorted_indices[:num_articles])

        return selected_indices
