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
    def get_disease_id_by_name(self, name: str) -> int:
        """
        :param name: Disease name
        :return: id of disease with given name
        """
        pass

    @abstractmethod
    def get_disease_id_by_icd10(self, icd10: str) -> list:
        """
        :param icd10:
        :return: id of disease with given icd10 code
        """
        pass

    @abstractmethod
    def get_disease_id_by_icd11(self, icd11: str) -> list:
        """
        :param icd11:
        :return: id of disease with given icd11 code
        """
        pass

    @abstractmethod
    def add_wiki_info(self, id_disease: int, language: str, title: str, link: str):
        """
        :param language:
        :param title:
        :param link:
        :param id_disease:
        """
        pass

    @abstractmethod
    def get_wiki_info(self, id_disease: int) -> list:
        """
        :param id_disease:
        """
        pass

    @abstractmethod
    def get_disease_info(self, id_disease: list) -> list:
        """
        :param id_disease:
        """
        pass

    @abstractmethod
    def get_icd10_info(self, icd10_code: str) -> list:
        """
        :param icd10_code:
        """
        pass

    @abstractmethod
    def get_icd11_info(self, icd11_code: str) -> list:
        """
        :param icd11_code:
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

    @abstractmethod
    def add_additional_info(self, id_disease: int, type: str, author: str, info: str):
        pass

    @abstractmethod
    def modify_additional_info(self, id_info: int, type: str, author: str, info: str):
        pass

    @abstractmethod
    def delete_additional_info(self, id_info: int):
        pass

    @abstractmethod
    def export_to_prolog(self) -> str:
        pass
