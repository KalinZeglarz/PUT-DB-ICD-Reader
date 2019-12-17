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

    def get_disease_id_by_name(self, name: str) -> int:
        """
        :param name: Disease name
        :return: id of disease with given name
        """
        cursor = self.database.cursor()
        cursor.execute("SELECT ID_DISEASE FROM DISEASES WHERE NAME='{0}';".format(name))
        id_disease = cursor.fetchall()
        cursor.close()
        return int(id_disease[0][0])

    def get_disease_id_by_icd10(self, icd10: str) -> int:
        """
        :param icd10:
        :return: id of disease with given icd10 code
        """
        icd10_split: list = icd10.split('.')
        while len(icd10_split) < 3:
            icd10_split.append('')
        cursor = self.database.cursor()
        cursor.execute(
            "SELECT ID_DISEASE FROM ICD_10 WHERE CATEGORY='{0}' and DETAILS='{1}' and EXTENSION='{2}';".format(
                icd10_split[0], icd10_split[1], icd10_split[2])
        )
        id_disease = cursor.fetchall()
        cursor.close()
        return int(id_disease[0][0])

    def get_disease_id_by_icd11(self, icd11: str) -> int:
        """
        :param icd11:
        :return: id of disease with given icd11 code
        """
        cursor = self.database.cursor()
        cursor.execute(
            "SELECT ID_DISEASE FROM ICD_11 WHERE CODE='{0}';".format(icd11)
        )
        id_disease = cursor.fetchall()
        cursor.close()
        return int(id_disease[0][0])

    def add_wiki_info(self, id_disease: int, language: str, title: str, link: str):
        """
        :param title:
        :param link:
        :param language:
        :param id_disease:
        """
        cursor = self.database.cursor()
        cursor.execute(
            "INSERT INTO WIKI VALUES ({0},'{1}','{2}','{3}')"
            "on duplicate key update LANGUAGE='{1}', TITLE='{2}', LINK='{3}';".format(id_disease, language, title, link)
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

    def get_wiki_info(self, id_disease: int) -> list:
        cursor = self.database.cursor()
        cursor.execute(
            "select LANGUAGE, TITLE, LINK from WIKI where ID_DISEASE={0}".format(id_disease)
        )
        wiki_info = cursor.fetchall()
        cursor.close()
        result: list = []
        for wiki_record in wiki_info:
            result.append({
                'lang': wiki_record[0],
                'title': wiki_record[1],
                'link': wiki_record[2]
            })
        return result

    def get_icd_10_info(self, icd10_code: str) -> dict:
        id_disease: int = self.get_disease_id_by_icd10(icd10_code)
        cursor = self.database.cursor()
        cursor.execute(
            "select CODE, NAME "
            "from  (select * from DISEASES where ID_DISEASE={0}) as SELECTED_CODE "
            "left join ICD_11 on SELECTED_CODE.ID_DISEASE = ICD_11.ID_DISEASE;".format(id_disease)
        )
        disease_info = cursor.fetchall()
        cursor.close()
        if len(disease_info) == 0:
            return {
                'icd10': None,
                'icd11': None,
                'diseaseName': None,
                'wikipedia': []
            }
        else:
            return {
                'icd10': icd10_code,
                'icd11': disease_info[0][0],
                'diseaseName': disease_info[0][1],
                'wikipedia': self.get_wiki_info(id_disease)
            }

    def get_icd_11_info(self, icd11_code: str) -> dict:
        id_disease: int = self.get_disease_id_by_icd11(icd11_code)
        cursor = self.database.cursor()
        cursor.execute(
            "select SELECTED_CODE.ID_DISEASE, CATEGORY, DETAILS, EXTENSION, NAME "
            "from  (select * from DISEASES where ID_DISEASE={0}) as SELECTED_CODE "
            "left join ICD_10 on SELECTED_CODE.ID_DISEASE = ICD_10.ID_DISEASE;".format(id_disease)
        )
        disease_info = cursor.fetchall()
        cursor.close()
        if len(disease_info) == 0:
            return {
                'icd10': None,
                'icd11': None,
                'diseaseName': None,
                'wikipedia': []
            }
        else:
            icd10_code: str = ''
            if disease_info[0][1] != '':
                icd10_code += disease_info[0][1]
                if disease_info[0][2] != '':
                    icd10_code += '.' + disease_info[0][2]
                    if disease_info[0][3] != '':
                        icd10_code += '.' + disease_info[0][3]
            return {
                'icd10': icd10_code,
                'icd11': icd11_code,
                'diseaseName': disease_info[0][4],
                'wikipedia': self.get_wiki_info(disease_info[0][0])
            }
