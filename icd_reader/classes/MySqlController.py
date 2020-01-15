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

    def add_disease_entry(self, name: str) -> None:
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
        if len(id_disease) == 0:
            return -1
        else:
            return int(id_disease[0][0])

    def get_disease_id_by_icd10(self, icd10: str) -> list:
        """
        :param icd10:
        :return: id of disease with given icd10 code
        """
        icd10_split: list = icd10.split('.')
        condition: str = "WHERE CATEGORY='{0}'".format(icd10_split[0])

        if len(icd10_split) >= 2:
            condition += " and DETAILS='{0}'".format(icd10_split[1])
        if len(icd10_split) >= 3:
            condition += " and EXTENSION='{0}'".format(icd10_split[2])

        cursor = self.database.cursor()
        cursor.execute(
            "SELECT ID_DISEASE FROM ICD_10 {0};".format(condition)
        )
        id_diseases = cursor.fetchall()
        cursor.close()
        if len(id_diseases) == 0:
            return []
        else:
            result: list = []
            for id_disease in id_diseases:
                result.append(id_disease[0])
            return result

    def get_disease_id_by_icd11(self, icd11: str) -> list:
        """
        :param icd11:
        :return: id of disease with given icd11 code
        """
        cursor = self.database.cursor()
        cursor.execute(
            "SELECT ID_DISEASE FROM ICD_11 WHERE CODE LIKE '{0}%';".format(icd11)
        )
        id_diseases = cursor.fetchall()
        cursor.close()
        if len(id_diseases) == 0:
            return []
        else:
            result: list = []
            for id_disease in id_diseases:
                result.append(id_disease[0])
            return result

    def add_wiki_info(self, id_disease: int, language: str, title: str, link: str) -> None:
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

    def get_additional_info(self, id_disease: int) -> list:
        cursor = self.database.cursor()
        cursor.execute(
            "select ID_ADDITIONAL_INFO, TYPE, AUTHOR, INFO from ADDITIONAL_INFO where ID_DISEASE={0}".format(id_disease)
        )
        additional_info = cursor.fetchall()
        cursor.close()
        result: list = []
        for info_record in additional_info:
            result.append({
                'infoId': info_record[0],
                'type': info_record[1],
                'author': info_record[2],
                'info': info_record[3]
            })
        return result

    def get_disease_info(self, id_diseases: list) -> list:
        diseases_info: list = []
        cursor = self.database.cursor()
        for id_disease in id_diseases:
            cursor.execute(
                "select SELECTED_CODE.ID_DISEASE, CATEGORY, DETAILS, EXTENSION, NAME, CODE "
                "from  (select * from DISEASES where ID_DISEASE={0}) as SELECTED_CODE "
                "left join ICD_10 on SELECTED_CODE.ID_DISEASE = ICD_10.ID_DISEASE "
                "left join ICD_11 on SELECTED_CODE.ID_DISEASE = ICD_11.ID_DISEASE".format(id_disease)
            )
            diseases_info.append(cursor.fetchall())
        cursor.close()
        if len(diseases_info) == 0:
            return []
        else:
            result: list = []
            for disease_info in diseases_info:
                icd10_code: str = ''
                if disease_info[0][1] != '':
                    icd10_code += disease_info[0][1]
                    if disease_info[0][2] != '':
                        icd10_code += '.' + disease_info[0][2]
                        if disease_info[0][3] != '':
                            icd10_code += '.' + disease_info[0][3]
                result.append({
                    'diseaseId': disease_info[0][0],
                    'diseaseName': disease_info[0][4],
                    'codes': {
                        'icd10': icd10_code,
                        'icd11': disease_info[0][5],
                    },
                    'wikipedia': self.get_wiki_info(disease_info[0][0]),
                    'additionalInfo': self.get_additional_info(disease_info[0][0])
                })
            return result

    def get_icd10_info(self, icd10_code: str) -> list:
        id_diseases: list = self.get_disease_id_by_icd10(icd10_code)
        return self.get_disease_info(id_diseases)

    def get_icd11_info(self, icd11_code: str) -> list:
        id_disease: list = self.get_disease_id_by_icd11(icd11_code)
        return self.get_disease_info(id_disease)

    def add_additional_info(self, id_disease: int, info_type: str, author: str, info: str) -> None:
        cursor = self.database.cursor()
        cursor.execute(
            "INSERT INTO ADDITIONAL_INFO VALUES ({0}, 0, '{1}','{2}','{3}')"
            "on duplicate key update TYPE='{1}', AUTHOR='{2}', INFO='{3}';".format(id_disease, info_type, author, info)
        )
        self.database.commit()
        cursor.close()

    def modify_additional_info(self, id_info: int, info_type: str, author: str, info: str) -> None:
        cursor = self.database.cursor()
        cursor.execute(
            "UPDATE ADDITIONAL_INFO "
            "SET TYPE='{1}', AUTHOR='{2}', INFO='{3}' "
            "WHERE ID_ADDITIONAL_INFO={0};".format(id_info, info_type, author, info)
        )
        self.database.commit()
        cursor.close()

    def delete_additional_info(self, id_info: int) -> None:
        cursor = self.database.cursor()
        cursor.execute(
            "DELETE FROM ADDITIONAL_INFO "
            "WHERE ID_ADDITIONAL_INFO={0};".format(id_info)
        )
        self.database.commit()
        cursor.close()

    def export_to_prolog(self) -> str:
        return ''
