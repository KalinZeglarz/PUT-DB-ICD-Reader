import re

from bs4 import BeautifulSoup

from icd_reader import logger

logger.initialize()


class HtmlParser:
    """Class used for getting desired data from Wikipedia pages HTML."""

    @staticmethod
    def find_icd_section_title(html: str, icd_10_code: str) -> str:
        """Finds link for disease section page on ICD-10 english page.

        :param html: html document
        :type html: str
        :param icd_10_code: ICD-10 code
        :type icd_10_code:
        :return: title of wikipedia article about given icd 10 code category
        :rtype: str
        """
        html_object: BeautifulSoup = BeautifulSoup(html, "html.parser")

        if html_object.title == "ICD-10 - Wikipedia":
            raise Exception("Not ICD-10 page")

        matches = re.findall("(([a-zA-Z]+)([0-9]+))(\\..+)?", icd_10_code)
        letter: str = matches[0][1].upper()

        links_in_table: list = html_object.select("table.wikitable td:nth-child(2) a")
        for disease_link in links_in_table:
            icd_range: str = disease_link.get_text()
            if letter not in icd_range:
                continue
            else:
                return disease_link.get("title")

        return ""

    @staticmethod
    def _find_disease_in_section(parent_element, icd_10_code: str) -> tuple:
        disease_sub_sections = parent_element.findAll("li", recursive=False)
        if disease_sub_sections is None:
            return None, None

        for sub_section in disease_sub_sections:
            if sub_section is None:
                continue

            disease_line = sub_section.findChildren("ul", recursive=False)
            if disease_line is not None:
                for ul in disease_line:
                    search_result = HtmlParser._find_disease_in_section(ul, icd_10_code)
                    if search_result[0] is not None:
                        return search_result

            line_texts = sub_section.findChildren("a", recursive=False)
            if line_texts is None:
                pass
            elif len(line_texts) < 2:
                pass
            elif icd_10_code in line_texts[0].get_text():
                article_link: str = line_texts[1].get("href")
                article_title: str = line_texts[1].get("title")
                return article_link, article_title
        return None, None

    @staticmethod
    def find_disease_name_and_link(html: str, icd_10_code: str) -> tuple:
        """Finds disease on disease section page and returns its link and title.

        :param html: html document
        :type html: str
        :param icd_10_code: ICD-10 code
        :type icd_10_code: str
        :return: link to article and its title
        :rtype: tuple
        """
        html_object: BeautifulSoup = BeautifulSoup(html, "html.parser")

        if html_object.title == "ICD-10 - Wikipedia":
            raise Exception("Not ICD-10 page")

        disease_sections: list = html_object.select("div:not(#toc) > ul")

        for section in disease_sections:
            article_link, article_title = HtmlParser._find_disease_in_section(section, icd_10_code.upper())
            if article_link is not None:
                return article_link, article_title
        return "", ""
