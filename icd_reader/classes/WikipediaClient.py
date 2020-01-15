import http.client
import json
import logging

from icd_reader import helpers, logger

logger.initialize()


class WikipediaClient:
    """Class used to communicate with Wikipedia API."""

    http_client: http.client.HTTPSConnection
    lang: str

    def __init__(self, language: str):
        """ Default constructor.

        :param language: Langueage of Wikipedia API (examples: en, pl)
        :type language:
        """
        self.lang = language

    def __del__(self):
        """Destructor. Closes connection to Wikipedia API (if any connections left).

        """
        self.http_client.close()

    def _connect_http_client(self) -> None:
        self.http_client = http.client.HTTPSConnection(self.lang + ".wikipedia.org", 443)

    def search_title(self, text: str) -> dict:
        """Searches Wikipedia for article with given text.

        :param text: text to be searched via wikipedia API
        :type text: str
        :return: search result in JSON format
        :rtype: dict
        """
        logging.info("Searching wikipedia for text '{0}'".format(text))
        url: str = "/w/api.php"
        http_params: dict = {
            "action": "query",
            "list": "search",
            "format": "json",
            "srsearch": text.replace(" ", "%20"),
            "srlimit": "1",
            "srprop": ""
        }
        url_with_params: str = helpers.add_http_parameters(url, http_params)

        self._connect_http_client()
        self.http_client.request("GET", url_with_params)
        response: bytes = self.http_client.getresponse().read()
        self.http_client.close()

        return json.loads(response)

    def get_languages(self, title: str) -> dict:
        """Queries Wikipedia API for a list of languages for given article.

        :param title: article title
        :type title: str
        :return: API response in JSON format
        :rtype: dict
        """
        logging.info("Searching wikipedia for languages for article with title '{0}'".format(title))
        url: str = "/w/api.php"
        http_params: dict = {
            "action": "query",
            "titles": title.replace(" ", "%20"),
            "prop": "langlinks",
            "format": "json",
            "llprop": "url"
        }
        url_with_params: str = helpers.add_http_parameters(url, http_params)

        self._connect_http_client()
        self.http_client.request("GET", url_with_params)
        response: bytes = self.http_client.getresponse().read()
        self.http_client.close()

        return json.loads(response)

    def get_article_language_info(self, title: str, language: str) -> tuple:
        """Queries wikipedia for language url for given article.

        :param title: Article language in short form (e.g.: en, pl, etc.)
        :type title: str
        :param language: Article language to be searched for (examples: en, pl)
        :type language: str
        :return: Link to and title of article in given language or empty strings if not found
        :rtype: tuple
        """
        logging.info("Searching wikipedia for '{0}' language for article with title '{1}'".format(language, title))
        url: str = "/w/api.php"
        http_params: dict = {
            "action": "query",
            "titles": title.replace(" ", "%20"),
            "prop": "langlinks",
            "format": "json",
            "llprop": "url|*",
            "lllang": language
        }
        url_with_params: str = helpers.add_http_parameters(url, http_params)

        self._connect_http_client()
        self.http_client.request("GET", url_with_params)
        response: bytes = self.http_client.getresponse().read()
        self.http_client.close()

        return WikipediaClient._get_language_info_from_json(json.loads(response), language)

    @staticmethod
    def _get_language_info_from_json(langlinks_response_json: dict, language: str) -> tuple:
        pages: dict = langlinks_response_json["query"]["pages"]
        langlinks: list = []
        for page in pages.values():
            if "langlinks" in page:
                langlinks = page["langlinks"]
        for langlink in langlinks:
            if langlink["lang"] == language:
                return langlink["url"], langlink["*"]
        return "", ""
