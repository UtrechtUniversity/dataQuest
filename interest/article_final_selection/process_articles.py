import pandas as pd
from interest.models.tfidf import TfidfEmbedder
from interest.article_final_selection.process_article import ArticleProcessor, clean
from interest.article_final_selection.article_selector import ArticleSelector
from sklearn.metrics.pairwise import cosine_similarity


def process_articles(articles_filepath:str, clean_keywords: list):
    articles_df = pd.read_csv(articles_filepath)

    article_bodies = []
    selected_indices = []
    for index , row in articles_df.iterrows():
        article_processor = ArticleProcessor(row['file_path'],row['article_id'])
        processed_article_body = article_processor.process_article(clean_keywords)
        if article_processor.selected:
            selected_indices.append(index)
        elif processed_article_body != "":
            article_bodies.append(processed_article_body)

    return article_bodies, selected_indices


def apply_tfidf_similarity(documents, keywords):
    model = TfidfEmbedder(ngram_max=1,
                          norm="l1",
                          sublinear_tf=False,
                          min_df=1,
                          max_df=1.0)

    keywords_list = [" ".join(keywords)]
    model.fit(documents)
    embeddings_documents = model.transform(documents).tocsr()
    embeddings_keywords = model.transform(keywords_list).tocsr()
    similarity_scores = cosine_similarity(embeddings_keywords, embeddings_documents)
    return similarity_scores[0]


def select_top_articles(similarity_scores,config):
    selector = ArticleSelector(similarity_scores, config)
    selected_indices = selector.select_articles()
    return selected_indices


def select_articles(articles_filepath: str, keywords: list, config:dict):
    clean_keywords = [clean(keyword) for keyword in keywords]
    article_bodies, selected_indices = process_articles(articles_filepath, clean_keywords)
    similarity_scores = apply_tfidf_similarity(article_bodies, clean_keywords)
    indices = select_top_articles(similarity_scores, config)
    selected_indices.extend(indices)

    return selected_indices
