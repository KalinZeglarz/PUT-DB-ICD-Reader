import re

from bs4 import BeautifulSoup


class HtmlParser:

    @staticmethod
    def find_icd_section_title(html: str, icd_code: str) -> str:
        """Finds link for disease section page on ICD-10 english page"""

        html_object: BeautifulSoup = BeautifulSoup(html, 'html.parser')

        if html_object.title == 'ICD-10 - Wikipedia':
            raise Exception("Not ICD-10 page")
            pass

        matches = re.findall('(([a-zA-Z]+)([0-9]+))(\\..+)?', icd_code)
        letter: str = matches[0][1].upper()

        links_in_table: list = html_object.select('table.wikitable td:nth-child(2) a')
        for disease_link in links_in_table:
            icd_range: str = disease_link.get_text()
            if letter not in icd_range:
                continue
            else:
                return disease_link.get('title')

        return ''

    @staticmethod
    def __find_disease_in_section(parent_element, icd_code: str) -> tuple:
        sub_disease_sections = parent_element.findAll('li')
        if sub_disease_sections is None:
            return None, None

        for sub_section in sub_disease_sections:
            if sub_section is None:
                continue

            disease_line = parent_element.findChildren('li', recursive=False)
            if disease_line is not None:
                for li in disease_line:
                    search_result = HtmlParser.__find_disease_in_section(li, icd_code)
                    if search_result is not None:
                        return search_result

            line_texts = sub_section.findChildren('a')
            for line_text in line_texts:
                if line_text.get_text() not in icd_code:
                    pass
                elif line_text.get_text() == icd_code:
                    return line_texts[1].get('href'), line_texts[1].get('title')

    @staticmethod
    def find_disease_name_and_link(html: str, icd_code: str) -> tuple:
        """Finds disease on disease section page and returns its link and title"""

        html_object: BeautifulSoup = BeautifulSoup(html, 'html.parser')

        if html_object.title == 'ICD-10 - Wikipedia':
            raise Exception("Not ICD-10 page")

        disease_sections: list = html_object.select('div:not(#toc) > ul')

        for section in disease_sections:
            search_result: tuple = HtmlParser.__find_disease_in_section(section, icd_code.upper())
            if search_result is not None:
                return search_result
