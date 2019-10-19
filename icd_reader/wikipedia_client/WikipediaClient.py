import http.client


class WikipediaClient:
    client: http.client.HTTPSConnection

    def __init__(self, lang: str):
        self.client = http.client.HTTPSConnection(lang + '.wikipedia.org', 443)
        pass

    def __del__(self):
        self.client.close()

    def search(self, text: str) -> http.client.HTTPResponse:
        """Searches Wikipedia with given text"""

        endpoint: str = '/w/api.php?'
        params: list = ['action=query', 'list=search', 'format=json', 'srsearch=' + text]
        i: int = 0
        while i < len(params):
            endpoint += params[i]
            if i < len(params) - 1:
                endpoint += '&'
            i += 1

        print(endpoint)
        self.client.request('GET', endpoint)

        return self.client.getresponse()
