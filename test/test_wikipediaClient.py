"""Unit tests for WikipediaClient class"""
from unittest import TestCase

from icd_mapper.classes.WikipediaClient import WikipediaClient


class TestWikipediaClient(TestCase):
    def test_constructor(self):
        wikipedia_client = WikipediaClient("pl")

        self.assertIsNotNone(wikipedia_client)

    def test_search(self):
        wikipedia_client = WikipediaClient("pl")
        response: dict = wikipedia_client.search_title("ICD-10 I40")

        self.assertIsNotNone(response)
        self.assertIsNotNone(response["query"]["search"])

    def test_get_languages(self):
        wikipedia_client = WikipediaClient("en")
        languages_json = wikipedia_client.get_languages("ICD-10")
        pages: dict = languages_json["query"]["pages"]
        langlinks: list = []
        for page in pages.values():
            langlinks = page["langlinks"]

        self.assertEqual(10, len(langlinks))

    def test_get_language_url_from_json(self):
        wikipedia_client = WikipediaClient("en")
        languages_json = wikipedia_client.get_languages("Grigori Rasputin")
        language_url, language_title = WikipediaClient._get_language_info_from_json(languages_json, "be")

        self.assertTrue("https://be.wikipedia.org/" in language_url)

    def test_get_article_language_url(self):
        wikipedia_client = WikipediaClient("en")
        language_url, language_title = wikipedia_client.get_article_language_info("ICD-10", "pl")

        self.assertTrue("https://pl.wikipedia.org/" in language_url)
