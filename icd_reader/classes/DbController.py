"""Contains definition of DbController abstract class."""

from abc import abstractmethod


class DbController:
    """Contains abstract methods used to save to and get data from data base"""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __del__(self):
        pass

    @abstractmethod
    def add_disease_entry(self, name: str):
        """
        :param name: Disease name
        """
        pass

    @abstractmethod
    def get_disease_id(self, name: str) -> int:
        """
        :param name: Disease name
        :return: id of disease with given name
        """
        pass

    @abstractmethod
    def add_wiki_info(self, id_disease: int, eng_title: str, pl_title: str, eng_link: str, pl_link: str):
        """
        :param id_disease:
        :param eng_title:
        :param pl_title:
        :param eng_link:
        :param pl_link:
        """
        pass

    @abstractmethod
    def add_icd_codes(self, id_disease: int, icd_10_code: list, icd_11_code: str):
        """
        :param id_disease:
        :param icd_10_code: ICD-10 code divided into category, details and extension
        :param icd_11_code:
        """
        pass
