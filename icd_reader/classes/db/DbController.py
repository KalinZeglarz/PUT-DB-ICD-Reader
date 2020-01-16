from abc import abstractmethod


class DbController:
    """Abstract class containing database interface."""

    @abstractmethod
    def __init__(self):
        """Default constructor. Should contain connection to database.

        """
        pass

    @abstractmethod
    def __del__(self):
        """Destructor. Should contain disconnection from database.

        """
        pass

    @abstractmethod
    def add_disease_entry(self, name: str) -> None:
        """Adds disease to database.

        :param name: disease name
        :type name: str
        :rtype: None
        """
        pass

    @abstractmethod
    def get_disease_id_by_name(self, name: str) -> int:
        """Searches database for disease with given name.

        :param name: disease name
        :type name: str
        :return: id of disease with given name
        :rtype: int
        """
        pass

    @abstractmethod
    def get_disease_id_by_icd10(self, icd10: str) -> list:
        """Searches database for disease with given ICD-10 code.

        :param icd10: ICD-10 code
        :type icd10: str
        :return: list of ids matching given icd10 code
        :rtype: list
        """
        pass

    @abstractmethod
    def get_disease_id_by_icd11(self, icd11: str) -> list:
        """Searches database for disease with given ICD-11 code.

        :param icd11: ICD-11 code
        :type icd11: str
        :return: list of ids matching given icd11 code
        :rtype: list
        """
        pass

    @abstractmethod
    def add_wiki_info(self, id_disease: int, language: str, title: str, link: str) -> None:
        """Adds Wikipedia information to database.

        :param id_disease: database id of disease
        :type id_disease: int
        :param language: language code (examples: en, pl, es)
        :type language: str
        :param title: article title
        :type title: str
        :param link: article link
        :type link: str
        :rtype: None
        """
        pass

    @abstractmethod
    def get_wiki_info(self, id_disease: int) -> list:
        """Searches database for Wikipedia information.

        :param id_disease: database id of disease
        :type id_disease: int
        :return: list of wikipedia information (language, article title, link)
        :rtype: list
        """
        pass

    @abstractmethod
    def get_disease_info(self, id_disease: list) -> list:
        """Searches database for all information concerning given disease.

        :param id_disease: list of database id of diseases
        :type id_disease: list
        :return: list of disease data
        :rtype: list
        """
        pass

    @abstractmethod
    def get_icd10_info(self, icd10_code: str) -> list:
        """Searches database for all information concerning given disease.

        :param icd10_code: ICD-10 code
        :type icd10_code: str
        :return: list of disease data
        :rtype: list
        """
        pass

    @abstractmethod
    def get_icd11_info(self, icd11_code: str) -> list:
        """Searches database for all information concerning given disease.

        :param icd11_code: ICD-11 code
        :type icd11_code: str
        :return: list of disease data
        :rtype: list
        """
        pass

    @abstractmethod
    def add_icd_codes(self, id_disease: int, icd_10_code: list, icd_11_code: str) -> None:
        """Adds ICD-10 and corresponding ICD-11 codes to database.

        :param id_disease: database id of disease
        :type id_disease: int
        :param icd_10_code: ICD-10 code divided into category, details and extension
        :type icd_10_code: list
        :param icd_11_code: ICD-11 code
        :type icd_11_code: str
        :rtype: None
        """
        pass

    @abstractmethod
    def add_additional_info(self, id_disease: int, info_type: str, author: str, info: str) -> None:
        """Adds additional information to disease.

        :param id_disease: database id of disease
        :type id_disease: int
        :param info_type: type of information (examples: comment, reference)
        :type info_type: str
        :param author: author of additional information
        :type author: str
        :param info: content of additional information
        :type info: str
        :rtype: None
        """
        pass

    @abstractmethod
    def modify_additional_info(self, id_info: int, info_type: str, author: str, info: str) -> None:
        """Adds additional information to disease.

        :param id_info: database id of additional information
        :type id_info: int
        :param info_type: type of information (examples: comment, reference)
        :type info_type: str
        :param author: author of additional information
        :type author: str
        :param info: content of additional information
        :type info: str
        :rtype: None
        """
        pass

    @abstractmethod
    def delete_additional_info(self, id_info: int) -> None:
        """Deletes additional information from disease.

        :param id_info: database id of additional information
        :type id_info: int
        :rtype: None
        """
        pass

    @abstractmethod
    def export_to_prolog(self) -> str:
        """TODO: No documentation yet

        """
        pass
