import unittest
import http.client
import json

from icd_reader.wikipedia_client.WikipediaClient import WikipediaClient


class TestWikipediaClient(unittest.TestCase):

    def test_constructor(self):
        client = WikipediaClient('pl')
        self.assertIsNotNone(client)

    def test_search(self):
        client = WikipediaClient('pl')
        response: http.client.HTTPResponse = client.search("ICD-10%20i40")
        self.assertIsNotNone(response)
        parsed: dict = json.loads(response.read())
        self.assertIsNotNone(parsed['query']['search'])
        print(parsed['query']['search'])


if __name__ == '__main__':
    unittest.main()

