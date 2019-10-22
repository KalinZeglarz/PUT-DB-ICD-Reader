from wikipedia import wikipedia

from icd_reader.html_parser.HtmlParser import HtmlParser
from icd_reader.wikipedia_client.WikipediaClient import WikipediaClient


class IcdReader:
    wikipedia_client: WikipediaClient

    def __init__(self, lang: str):
        self.wikipedia_client = WikipediaClient(lang)

    def __del__(self):
        pass

    def get_disease_wikipedia_data(self, icd_code: str) -> tuple:
        icd_code_upper: str = icd_code.upper()
        icd_10_search_result: dict = self.wikipedia_client.search('ICD-10')
        icd_list_page_title: str = icd_10_search_result['query']['search'][0]['title']
        icd_list_page_html: str = str(wikipedia.page(icd_list_page_title).html())

        disease_group_page_title: str = HtmlParser.find_icd_section_title(icd_list_page_html, icd_code_upper)
        disease_group_page_html: str = str(wikipedia.page(disease_group_page_title).html())

        url, title = HtmlParser.find_disease_name_and_link(disease_group_page_html, icd_code_upper)

        polish_language_url: str = self.wikipedia_client.get_article_language_url(title, 'pl')

        return title, 'https://en.wikipedia.org' + url, polish_language_url
