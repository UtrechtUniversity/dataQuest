import gzip
import json
import logging

from interest.preprocessor.text_cleaner import TextCleaner


def clean(text):
    text_cleaner = TextCleaner()
    return text_cleaner.preprocess(text)


class ArticleProcessor:
    def __init__(self,gzip_file_path, article_id):
        self._file_path = gzip_file_path
        self._article_id = article_id
        self._title = ''
        self._body = ''
        self.selected = False

    def _read_article_from_gzip(self):
        try:
            with gzip.open(self._file_path, 'rt') as f:
                data = json.load(f)
                articles = data.get('articles', {})
                article = articles.get(str(self._article_id), {})
                title = article.get('title', {})
                body = article.get('body', {})
                body_string = " ".join(body)
                return title, body_string
        except Exception as e:
            logging.error(f"Error reading article {self._article_id} from {self._file_path}: {e}")
            return None, None

    def process_article(self, clean_keywords):
        self._title, self._body = self._read_article_from_gzip()
        if (self._title is None) or (self._body is None):
            return ""
        clean_title = clean(self._title)
        title_with_keyword = any(keyword in clean_title for keyword in clean_keywords)
        if title_with_keyword:
            self.selected = True
            return ""
        else:
            return clean(self._body)


