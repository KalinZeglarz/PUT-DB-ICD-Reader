import http.client

from icd_reader.wikipedia_client import helpers


class WikipediaClient:
    http_client: http.client.HTTPSConnection

    def __init__(self, lang: str):
        self.http_client = http.client.HTTPSConnection(lang + '.wikipedia.org', 443)
        pass

    def __del__(self):
        self.http_client.close()

    def search(self, text: str) -> http.client.HTTPResponse:
        """Searches Wikipedia with given text"""

        endpoint: str = '/w/api.php'
        http_params: dict = {
            'action': 'query',
            'list': 'search',
            'format': 'json',
            'srsearch': text
        }
        endpoint_with_params: str = helpers.add_http_parameters(endpoint, http_params)
        print(endpoint_with_params)
        self.http_client.request('GET', endpoint_with_params)

        return self.http_client.getresponse()
