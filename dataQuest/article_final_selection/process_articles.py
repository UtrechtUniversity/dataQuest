"""
This module contains functions for selecting articles based on keywords
and similarity scores.
"""
from typing import List, Tuple, Dict, Union
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from dataQuest.models.tfidf import TfidfEmbedder
from dataQuest.article_final_selection.process_article import ArticleProcessor
from dataQuest.article_final_selection.process_article import clean
from dataQuest.article_final_selection.article_selector import ArticleSelector


def process_articles(articles_filepath: str, clean_keywords: List[str]) -> (
        Tuple)[List[str], List[int]]:
    """
    Process articles from a CSV file.

    Args:
        articles_filepath (str): The path to the CSV file containing articles.
        clean_keywords (List[str]): A list of clean keywords.

    Returns:
        Tuple[List[str], List[int]]: A tuple containing the processed article
         bodies and selected indices.
    """
    articles_df = pd.read_csv(articles_filepath)
    article_bodies: List[str] = []
    selected_indices: List[int] = []
    for index, row in articles_df.iterrows():
        article_processor = ArticleProcessor(row['file_path'],
                                             row['article_id'])
        processed_article_body = article_processor.process_article(
                                                   clean_keywords)
        if article_processor.selected:
            selected_indices.append(int(str(index)))
        elif processed_article_body != "":
            article_bodies.append(processed_article_body)
    return article_bodies, selected_indices


def apply_tfidf_similarity(documents: List[str], keywords: List[str]) -> (
        List)[float]:
    """
    Apply TF-IDF similarity between documents and keywords.

    Args:
        documents (List[str]): A list of document bodies.
        keywords (List[str]): A list of keywords.

    Returns:
        List[float]: A list of similarity scores.
    """
    model = TfidfEmbedder(ngram_max=1, norm="l2", sublinear_tf=False, min_df=1,
                          max_df=1.0)
    keywords_list = [" ".join(keywords)]
    model.fit(documents)
    embeddings_documents = model.transform(documents).tocsr()
    embeddings_keywords = model.transform(keywords_list).tocsr()
    avg_keywords_embedding = embeddings_keywords.mean(axis=0)
    avg_keywords_embedding = np.asarray(avg_keywords_embedding).flatten()
    similarity_scores = cosine_similarity([avg_keywords_embedding],
                                          embeddings_documents)
    return similarity_scores[0]


def select_top_articles(similarity_scores: List[float],
                        config: Dict[str, Union[str, float, int]]) \
                        -> List[int]:
    """
    Select top articles based on similarity scores and configuration.

    Args:
        similarity_scores (List[float]): A list of similarity scores.
        config (Dict[str, str]): Configuration for selecting articles.

    Returns:
        List[int]: A list of selected article indices.
    """
    selector = ArticleSelector(similarity_scores, config)
    selected_indices = selector.select_articles()
    return selected_indices


def select_articles(articles_filepath: str, keywords: List[str],
                    config: Dict[str, Union[str, float, int]]) -> List[int]:
    """
    Select articles based on keywords, similarity scores, and configuration.

    Args:
        articles_filepath (str): The path to the CSV file containing articles.
        keywords (List[str]): A list of keywords.
        config (Dict[str, str]): Configuration for selecting articles.

    Returns:
        List[int]: A list of selected article indices.
    """
    clean_keywords = [clean(keyword) for keyword in keywords]
    article_bodies, selected_indices = process_articles(articles_filepath,
                                                        clean_keywords)
    similarity_scores = apply_tfidf_similarity(article_bodies, clean_keywords)
    indices = select_top_articles(similarity_scores, config)
    selected_indices.extend(indices)
    return selected_indices
