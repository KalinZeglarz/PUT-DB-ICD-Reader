import http.client
import json
from unittest import TestCase

from icd_reader.wikipedia_client.WikipediaClient import WikipediaClient


class TestWikipediaClient(TestCase):
    def test_constructor(self):
        wikipedia_client = WikipediaClient('pl')
        self.assertIsNotNone(wikipedia_client)

    def test_search(self):
        wikipedia_client = WikipediaClient('pl')
        response: http.client.HTTPResponse = wikipedia_client.search("ICD-10%20i40")
        self.assertIsNotNone(response)
        parsed_response_content: dict = json.loads(response.read())
        self.assertIsNotNone(parsed_response_content['query']['search'])
        print(parsed_response_content['query']['search'])
