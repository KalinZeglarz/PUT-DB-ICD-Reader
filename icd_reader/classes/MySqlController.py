"""Contains implementation of MySqlController class."""

from typing import Union

import mysql.connector

from icd_reader.classes.DbController import DbController


class MySqlController(DbController):
    """Contains implementation of methods defined by DbController using MySQL"""
    database: Union

    def __init__(self, host: str, user: str, password: str):
        super().__init__()
        self.database = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database='icd_service'
        )

    def __del__(self):
        self.database.close()

    def add_disease_entry(self, name: str):
        """
        :param name: Disease name
        """
        cursor = self.database.cursor()
        cursor.execute("INSERT INTO DISEASES (NAME) VALUES ('{0}') on duplicate key update NAME='{0}';".format(name))
        self.database.commit()
        cursor.close()

    def get_disease_id(self, name: str) -> int:
        """
        :param name: Disease name
        :return: id of disease with given name
        """
        cursor = self.database.cursor()
        cursor.execute("SELECT ID_DISEASE FROM DISEASES WHERE NAME='{0}';".format(name))
        id_disease = cursor.fetchall()
        cursor.close()
        return int(id_disease[0][0])

    def add_wiki_info(self, id_disease: int, eng_title: str, pl_title: str, eng_link: str, pl_link: str):
        """
        :param id_disease:
        :param eng_title:
        :param pl_title:
        :param eng_link:
        :param pl_link:
        """
        cursor = self.database.cursor()
        cursor.execute(
            "INSERT INTO WIKI VALUES ({0},'{1}','{2}','{3}','{4}')"
            "on duplicate key update ENG_TITLE='{1}', PL_TITLE='{2}', ENG_LINK='{3}', PL_LINK='{4}';".format(
                id_disease, eng_title, pl_title, eng_link, pl_link)
        )
        self.database.commit()
        cursor.close()

    def add_icd_codes(self, id_disease: int, icd_10_code: list, icd_11_code: str):
        """
        :param id_disease:
        :param icd_10_code: ICD-10 code divided into category, details and extension
        :param icd_11_code:
        """
        cursor = self.database.cursor()
        cursor.execute(
            "INSERT INTO ICD_10 VALUES ({0},'{1}','{2}','{3}') "
            "on duplicate key update CATEGORY='{1}', DETAILS='{2}', EXTENSION='{3}';".format(id_disease, icd_10_code[0],
                                                                                             icd_10_code[1],
                                                                                             icd_10_code[2])
        )
        cursor.close()
        cursor = self.database.cursor()
        cursor.execute(
            "INSERT INTO ICD_11 VALUES ({0},'{1}') on duplicate key update CODE='{1}';".format(id_disease, icd_11_code)
        )
        cursor.close()
        self.database.commit()
