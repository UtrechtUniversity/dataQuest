import argparse
import logging
from pathlib import Path
import pandas as pd
from interest.utils import get_keywords_from_config
from interest.utils import get_article_selector_from_config
from interest.article_final_selection.process_articles import select_articles


def update_selected_indices_in_file(filepath, indices_selected):
    try:
        # Check if indices_selected is not empty and all indices are non-negative integers
        if indices_selected and all(isinstance(idx, int) and idx >= 0 for idx in indices_selected):
            df = pd.read_csv(filepath)
            df['selected'] = 0
            df.loc[indices_selected, 'selected'] = 1
            df.to_csv(filepath, index=False)
        else:
            print(indices_selected)
            logging.error("Invalid indices_selected")
    except Exception as e:
        logging.error("Error updating selected indices in file: %s",e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Select final articles.")

    parser.add_argument(
        "--input_dir",
        type=Path,
        required=True,
        help="Base directory for reading input files.",
    )
    parser.add_argument(
        "--glob",
        type=str,
        default="*.csv",
        help="Glob pattern for find input files; e.g. '*.csv'.",
    )
    parser.add_argument(
        "--config_path",
        type=Path,
        default="config.json",
        help="File path of config file.",
    )

    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"Not a directory: '{str(args.input_dir.absolute())}'")

    keywords = get_keywords_from_config(args.config_path)
    config_article_selector = get_article_selector_from_config(args.config_path)

    if (len(keywords) >0) and (config_article_selector):
        for articles_filepath in args.input_dir.rglob(args.glob):
            selected_indices = select_articles(articles_filepath, keywords, config_article_selector)
            update_selected_indices_in_file(articles_filepath,selected_indices)

