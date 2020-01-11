"""Contains implementation of WikipediaClient class."""

import http.client
import json
import logging

from icd_reader import helpers, logger

logger.initialize()


class WikipediaClient:
    """Contains methods used to communicate with wikipedia API"""

    http_client: http.client.HTTPSConnection
    lang: str

    def __init__(self, lang: str):
        self.lang = lang

    def __del__(self):
        self.http_client.close()

    def _connect_http_client(self):
        self.http_client = http.client.HTTPSConnection(self.lang + ".wikipedia.org", 443)

    def search_title(self, text: str) -> dict:
        """
        Searches Wikipedia with given text.

        :param text: Text to be searched via wikipedia API
        :return: Search result in JSON format
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
        """
        Queries wikipedia for a list of languages for given article.

        :param title: Article title
        :return: API response in JSON format
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

    def get_article_language_info(self, title: str, lang: str) -> tuple:
        """
        Queries wikipedia for language url for given article.

        :param title: Article language in short form (e.g.: en, pl, etc.)
        :param lang: Article language to be searched for
        :return: Link to article in given language or empty string if not found
        """
        logging.info("Searching wikipedia for '{0}' language for article with title '{1}'".format(lang, title))
        url: str = "/w/api.php"
        http_params: dict = {
            "action": "query",
            "titles": title.replace(" ", "%20"),
            "prop": "langlinks",
            "format": "json",
            "llprop": "url|*",
            "lllang": lang
        }
        url_with_params: str = helpers.add_http_parameters(url, http_params)

        self._connect_http_client()
        self.http_client.request("GET", url_with_params)
        response: bytes = self.http_client.getresponse().read()
        self.http_client.close()

        return WikipediaClient.get_language_info_from_json(json.loads(response), lang)

    @staticmethod
    def get_language_info_from_json(langlinks_response_json: dict, language: str) -> tuple:
        """
        Extracts url for page in given language from langlinks api response.

        :param langlinks_response_json:  Response from langlinks wikipedia query
        :param language: Language to be searched in langlinks response
        :return: Link to article in given language or empty string if not found
        """
        pages: dict = langlinks_response_json["query"]["pages"]
        langlinks: list = []
        for page in pages.values():
            if "langlinks" in page:
                langlinks = page["langlinks"]
        for langlink in langlinks:
            if langlink["lang"] == language:
                return langlink["url"], langlink["*"]
        return "", ""
