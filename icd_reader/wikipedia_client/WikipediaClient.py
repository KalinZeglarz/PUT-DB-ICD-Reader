import http.client


class WikipediaClient:
    http_client: http.client.HTTPSConnection

    def __init__(self, lang: str):
        self.http_client = http.client.HTTPSConnection(lang + '.wikipedia.org', 443)
        pass

    def __del__(self):
        self.http_client.close()

    def search(self, text: str) -> http.client.HTTPResponse:
        """Searches Wikipedia with given text"""

        endpoint: str = '/w/api.php?'
        http_params: list = ['action=query', 'list=search', 'format=json', 'srsearch=' + text]
        params_index: int = 0
        while params_index < len(http_params):
            endpoint += http_params[params_index]
            if params_index < len(http_params) - 1:
                endpoint += '&'
            params_index += 1

        print(endpoint)
        self.http_client.request('GET', endpoint)

        return self.http_client.getresponse()
