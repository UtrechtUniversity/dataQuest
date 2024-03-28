class ArticleSelector:
    def __init__(self, similarity_scores, config):
        self.similarity_scores = similarity_scores
        self.config = config

    def select_articles(self):
        sorted_indices = sorted(
            range(len(self.similarity_scores)),
            key=lambda i: self.similarity_scores[i],
            reverse=True
        )

        selected_indices = []
        if self.config["type"] == "threshold":
            threshold = float(self.config["value"])
            selected_indices.extend(
                i for i, score in enumerate(self.similarity_scores) if score >= threshold
            )
        elif self.config["type"] == "num_articles":
            num_articles = int(self.config["value"])
            selected_indices.extend(sorted_indices[:num_articles])

        return selected_indices
