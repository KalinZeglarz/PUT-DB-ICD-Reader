import json
import logging
import re
from collections import OrderedDict

from wikipedia import wikipedia

from icd_mapper import logger
from icd_mapper.classes.HtmlParser import HtmlParser
from icd_mapper.classes.WikipediaClient import WikipediaClient

logger.initialize()


class IcdWikipediaMapper:
    """Class used for mapping ICD-10 code with Wikipedia articles."""

    wikipedia_client: WikipediaClient
    icd_chapter_map: dict
    wikipedia_pages_cache: OrderedDict = OrderedDict()

    def __init__(self, code_spaces_path: str):
        """Loads codespaces for ICD-10 category articles.

        :param code_spaces_path: path to file with wikipedia article codespaces
        :type code_spaces_path: str
        """
        self.wikipedia_client = WikipediaClient("en")
        self._load_code_spaces_json(code_spaces_path)

    def __del__(self):
        pass

    def _load_code_spaces_json(self, code_spaces_path: str) -> None:
        file = open(code_spaces_path, "r")
        json_text = file.read()
        file.close()
        self.icd_chapter_map = json.loads(json_text)

    def _get_icd_10_article_chapter(self, icd10_code: str) -> str:
        for entry in self.icd_chapter_map["codeSpaces"]:
            code_space: str = entry["codeSpace"]
            code_space_search = re.search("([A-Z])([0-9]+)-([A-Z])([0-9]+)", code_space, re.IGNORECASE)
            icd10_code_search = re.search("([A-Z])([0-9]+)(\\.[0-9]+)*", icd10_code, re.IGNORECASE)
            code_letters: list = [code_space_search.group(1), code_space_search.group(3)]
            code_numbers: list = [code_space_search.group(2), code_space_search.group(4)]
            if code_letters[0] == code_letters[1] and code_letters[0] == icd10_code_search.group(1):
                if int(code_numbers[0]) <= int(icd10_code_search.group(2)) <= int(code_numbers[1]):
                    return entry["wikipediaChapter"]
            else:
                if code_letters[0] == icd10_code_search.group(1):
                    if int(code_numbers[0]) <= int(icd10_code_search.group(2)) <= 99:
                        return entry["wikipediaChapter"]
                elif code_letters[1] == icd10_code_search.group(1):
                    if 0 <= int(icd10_code_search.group(2)) <= int(code_numbers[1]):
                        return entry["wikipediaChapter"]
        return "not found"

    def _get_icd_chapter_article_title(self, icd10_code: str) -> str:
        icd_10_wikipedia_chapter = self._get_icd_10_article_chapter(icd10_code)
        if icd_10_wikipedia_chapter == "not found":
            return "not found"
        icd_10_chapter_search_str: str = "Chapter {} of ICD-10 deals with".format(icd_10_wikipedia_chapter)
        icd_10_search_result: dict = self.wikipedia_client.search_title(icd_10_chapter_search_str)
        return icd_10_search_result["query"]["search"][0]["title"]

    def _get_icd_chapter_article_page(self, title: str) -> str:
        if title in self.wikipedia_pages_cache:
            return self.wikipedia_pages_cache[title]

        result: str = str(wikipedia.page(title).html())
        self.wikipedia_pages_cache[title] = result
        if len(self.wikipedia_pages_cache) > 4:
            # Removes oldest page in cache
            self.wikipedia_pages_cache.popitem(False)
        return result

    def get_disease_wikipedia_data(self, icd10_code: str, languages: list = None) -> list:
        """Searches for article about disease with given ICD-10 code.

        :param icd10_code: ICD-10 code
        :type icd10_code: str
        :param languages: Article languages to be searched for (examples: en, es, ru, pl)
        :type languages: list
        :return: article title and link to english and polish version of article
        :rtype: list
        """
        if languages is None:
            languages = []
        icd10_code = icd10_code.upper()
        icd_code_upper: str = icd10_code.upper()

        icd_chapter_article_title: str = self._get_icd_chapter_article_title(icd10_code)
        if icd_chapter_article_title == 'not found':
            return []

        disease_group_article_html: str = self._get_icd_chapter_article_page(icd_chapter_article_title)

        url, title = HtmlParser.find_disease_name_and_link(disease_group_article_html, icd_code_upper)

        if url == "":
            return []

        result: list = [('en', title, "https://en.wikipedia.org" + url)]

        title_search_response = self.wikipedia_client.search_title(title)
        if len(title_search_response["query"]["search"]) > 0:
            title = title_search_response["query"]["search"][0]["title"]

            for language in languages:
                language_url, language_title = self.wikipedia_client.get_article_language_info(
                    title.replace("'s", ""), language)
                if language_url != "":
                    result.append((language, language_title, language_url))

        logging.debug("Article title for ICD-10 code '{}' is '{}'".format(icd10_code, title))
        logging.debug("Articles urls for ICD-10 code '{}' is '{}'".format(icd10_code, result))
        return result

    def get_diseases_wikipedia_data(self, icd10_code_list: list, languages: list = None) -> list:
        """Searches for articles about diseases with given ICD-10 codes.

        :param icd10_code_list: list of ICD-10 codes
        :type icd10_code_list: list
        :param languages: Article languages to be searched for (examples: en, es, ru, pl)
        :type languages: list
        :return: list of article title and link to english and other versions of article
        :rtype: list
        """
        if languages is None:
            languages = []
        result: list = []
        for icd10_code in icd10_code_list:
            data_search_result: list = self.get_disease_wikipedia_data(icd10_code, languages)
            if not data_search_result:
                logging.info("Code '{}' not found".format(icd10_code))
            elif data_search_result[0]:
                result.append(data_search_result)
            elif data_search_result[0] == "":
                logging.info("Code '{}' article not found".format(icd10_code))
        return result
