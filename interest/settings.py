"""
Module containing configuration settings for the project.
"""
import os

SPACY_MODEL = os.getenv("SPACY_MODEL", "nl_core_news_sm")
"""Spacy model to use for sentence splitting."""

ENCODING = os.getenv("ENCODING", "utf-8")
"""Encoding used for reading and writing files."""
