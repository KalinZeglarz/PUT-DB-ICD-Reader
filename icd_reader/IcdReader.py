"""Contains implementation of IcdReader class."""

from wikipedia import wikipedia

from icd_reader.icd_mapper.HtmlParser import HtmlParser
from icd_reader.icd_mapper.WikipediaClient import WikipediaClient


class IcdReader:
    """Handles readings of ICD codes and getting data bout it from wikipedia."""

    wikipedia_client: WikipediaClient

    def __init__(self):
        self.wikipedia_client = WikipediaClient('en')

    def __del__(self):
        pass

    def get_disease_wikipedia_data(self, icd_10_code: str) -> tuple:
        """
        Searches for article about disease with given ICD 10 code.

        :param icd_10_code:
        :return: article title and link to english and polish version of article
        """
        icd_code_upper: str = icd_10_code.upper()
        icd_10_search_result: dict = self.wikipedia_client.search('ICD-10')
        icd_list_page_title: str = icd_10_search_result['query']['search'][0]['title']
        icd_list_page_html: str = str(wikipedia.page(icd_list_page_title).html())

        disease_group_page_title: str = HtmlParser.find_icd_section_title(icd_list_page_html, icd_code_upper)
        disease_group_page_html: str = str(wikipedia.page(disease_group_page_title).html())

        url, title = HtmlParser.find_disease_name_and_link(disease_group_page_html, icd_code_upper)

        polish_language_url: str = self.wikipedia_client.get_article_language_url(title, 'pl')
        english_language_url: str = 'https://en.wikipedia.org' + url

        return title, english_language_url, polish_language_url
