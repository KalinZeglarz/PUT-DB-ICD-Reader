import http.client
import json

from icd_reader import helpers


class WikipediaClient:
    """Contains methods used to communicate with wikipedia API"""

    http_client: http.client.HTTPSConnection

    def __init__(self, lang: str):
        self.http_client = http.client.HTTPSConnection(lang + '.wikipedia.org', 443)
        pass

    def __del__(self):
        self.http_client.close()

    def search(self, text: str) -> dict:
        """Searches Wikipedia with given text"""

        endpoint: str = '/w/api.php'
        http_params: dict = {
            'action': 'query',
            'list': 'search',
            'format': 'json',
            'srsearch': text.replace(' ', '%20')
        }
        endpoint_with_params: str = helpers.add_http_parameters(endpoint, http_params)
        self.http_client.request('GET', endpoint_with_params)

        response: bytes = self.http_client.getresponse().read()
        return json.loads(response)

    def get_languages(self, title: str) -> dict:
        """Queries wikipedia for a list of languages for given article"""

        endpoint: str = '/w/api.php'
        http_params: dict = {
            'action': 'query',
            'titles': title.replace(' ', '%20'),
            'prop': 'langlinks',
            'format': 'json',
            'llprop': 'url'
        }
        endpoint_with_params: str = helpers.add_http_parameters(endpoint, http_params)
        self.http_client.request('GET', endpoint_with_params)

        response: bytes = self.http_client.getresponse().read()
        return json.loads(response)

    def get_article_language_url(self, title: str, lang: str) -> str:
        """Queries wikipedia for language url for given article"""

        endpoint: str = '/w/api.php'
        http_params: dict = {
            'action': 'query',
            'titles': title.replace(' ', '%20'),
            'prop': 'langlinks',
            'format': 'json',
            'llprop': 'url',
            'lllang': lang
        }
        endpoint_with_params: str = helpers.add_http_parameters(endpoint, http_params)
        self.http_client.request('GET', endpoint_with_params)

        response: bytes = self.http_client.getresponse().read()

        return WikipediaClient.get_language_url_from_json(json.loads(response), lang)

    @staticmethod
    def get_language_url_from_json(langlinks_response_json: dict, language: str) -> str:
        """Extracts url for page in given language from langlinks api response"""

        pages: dict = langlinks_response_json['query']['pages']
        langlinks: list = []
        for page in pages.values():
            langlinks = page['langlinks']
        for langlink in langlinks:
            if langlink['lang'] == language:
                return langlink['url']
        return ''
