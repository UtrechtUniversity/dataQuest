from interest.document_filter import YearFilter, TitleFilter, DocumentFilter
from interest.document_filter import (CompoundFilter, DecadeFilter,
                                      KeywordsFilter)
# from sklearn.feature_extraction.text import CountVectorizer
import json
from typing import List
# import os

# def calculate_word_frequency_per_doc(document):
#     # Initialize CountVectorizer
#     vectorizer = CountVectorizer()
#
#     # Fit the vectorizer to the document and transform the document
#     # into a word frequency matrix
#     word_frequency_matrix = vectorizer.fit_transform([document])
#
#     # Get the vocabulary (list of words) and their corresponding indices
#     vocabulary = vectorizer.get_feature_names_out()
#
#     # Get the word frequency vector for the document
#     word_frequency_vector = word_frequency_matrix.toarray()[0]
#
#     # Create a dictionary mapping words to their frequencies
#     word_frequency_dict = dict(zip(vocabulary,
#                           word_frequency_vector.tolist()))
#
#     return word_frequency_dict


def load_filters_from_config(config_file) -> CompoundFilter:
    with open(config_file, 'r') as f:
        config = json.load(f)

    filters: List[DocumentFilter] = []
    for filter_config in config['filters']:
        filter_type = filter_config['type']
        if filter_type == 'TitleFilter':
            filters.append(TitleFilter(filter_config['title']))
        elif filter_type == 'YearFilter':
            filters.append(YearFilter(filter_config['year']))
        elif filter_type == 'DecadeFilter':
            filters.append(DecadeFilter(filter_config['decade']))
        elif filter_type == 'KeywordsFilter':
            filters.append(KeywordsFilter(filter_config['keywords']))

    return CompoundFilter(filters)


# def save_filtered_articles(input_file,article_id,word_freq,output_dir)
# -> None:
#
#     data = {
#         "file_path": str(input_file.filepath),
#         "article_id": str(article_id),
#         "Date": str(input_file.doc().publish_date),
#         "Title": input_file.doc().title,
#         "word_freq": word_freq
#     }
#
#     output_fp = os.path.join(output_dir, input_file.base_file_name()+'.json')
#     print('output_fp',output_fp)
#     with open(output_fp, "w") as json_file:
#         json.dump(data, json_file, indent=4)
