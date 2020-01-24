"""Contains implementation of SqlController class."""

from typing import List, Tuple

from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from icd_mapper.classes.db.DbController import DbController
from icd_mapper.classes.db.sql_orm import *


class SqlController(DbController):
    """Contains implementation of methods defined by DbController using SQL"""

    engine: Engine
    Session: sessionmaker

    def __init__(self, database: str, host: str, user: str, password: str):
        super().__init__()
        self.engine = create_engine(
            "{}://{}:{}@{}/icd_service".format(database, user, password, host),
            pool_recycle=3600
        )
        self.Session = sessionmaker(bind=self.engine)
        self.db_session = scoped_session(sessionmaker(autocommit=False,
                                                      autoflush=False,
                                                      bind=self.engine))

    def __del__(self):
        self.engine.dispose()

    def add_disease_entry(self, name: str) -> None:
        session: Session = self.db_session()
        if not session.query(Disease).filter(Disease.name == name).first():
            disease = Disease(name=name)
            session.add(disease)
            session.commit()
        session.close()

    def get_disease_id_by_name(self, name: str) -> int:
        session: Session = self.db_session()
        id_disease: List[Disease] = session.query(Disease.id_disease) \
            .filter(Disease.name == name) \
            .all()
        session.close()

        if len(id_disease) == 0:
            return -1
        else:
            return int(id_disease[0].id_disease)

    def get_disease_id_by_icd10(self, icd10: str) -> list:
        icd10_split: list = icd10.split('.')
        while len(icd10_split) < 3:
            icd10_split.append('')

        session = self.db_session()
        icd10_list: List[Icd10] = session.query(Icd10.id_disease) \
            .filter(Icd10.category == icd10_split[0],
                    Icd10.details.startswith(icd10_split[1]),
                    Icd10.extension.startswith(icd10_split[2])) \
            .all()
        session.close()

        if len(icd10_list) == 0:
            return []
        else:
            result: list = []
            for icd10 in icd10_list:
                result.append(icd10.id_disease)
            return result

    def get_disease_id_by_icd11(self, icd11: str) -> list:
        session = self.db_session()
        id_diseases: List[Icd11] = session.query(Icd11.id_disease) \
            .filter(Icd11.code == icd11) \
            .all()
        session.close()

        if len(id_diseases) == 0:
            return []
        else:
            result: list = []
            for id_disease in id_diseases:
                result.append(id_disease.id_disease)
            return result

    def add_wiki_info(self, id_disease: int, language: str, title: str, link: str) -> None:
        session: Session = self.db_session()
        wiki_on_db: Wiki = session.query(Wiki) \
            .filter(Wiki.id_disease == id_disease, Wiki.language == language).first()
        if not wiki_on_db:
            wiki = Wiki(id_disease=id_disease, language=language, title=title, link=link)
            session.add(wiki)
        else:
            wiki_on_db.title = title
            wiki_on_db.link = link
        session.commit()
        session.close()

    def add_icd_codes(self, id_disease: int, icd10_code: list, icd11_code: str):
        icd10 = Icd10(id_disease=id_disease, category=icd10_code[0], details=icd10_code[1], extension=icd10_code[2])
        icd11 = Icd11(id_disease=id_disease, code=icd11_code)

        session: Session = self.db_session()
        session.merge(icd10)
        session.merge(icd11)
        session.commit()
        session.close()

    def get_wiki_info(self, id_disease: int) -> list:
        session = self.db_session()
        wiki_list: List[Wiki] = session.query(Wiki) \
            .filter(Wiki.id_disease == id_disease) \
            .all()
        session.close()
        result: list = []
        for wiki in wiki_list:
            result.append({
                'lang': wiki.language,
                'title': wiki.title,
                'link': wiki.link
            })
        return result

    def get_additional_info(self, id_disease: int) -> list:
        session: Session = self.db_session()
        additional_info: List[AdditionalInfo] = session.query(AdditionalInfo) \
            .filter(AdditionalInfo.id_disease == id_disease) \
            .all()
        session.close()

        result: list = []
        for info_record in additional_info:
            result.append({
                'infoId': info_record.id_additional_info,
                'type': info_record.type,
                'author': info_record.author,
                'info': info_record.info
            })
        return result

    def get_disease_info(self, id_diseases: list) -> list:
        diseases_info: List[Tuple[Disease, Icd10, Icd11]] = []
        session: Session = self.db_session()
        for id_disease in id_diseases:
            disease: Disease = session.query(Disease) \
                .filter(Disease.id_disease == id_disease)[0]
            icd10: Icd10 = session.query(Icd10) \
                .filter(Icd10.id_disease == id_disease)[0]
            icd11: Icd11 = session.query(Icd11) \
                .filter(Icd11.id_disease == id_disease)[0]
            diseases_info.append((disease, icd10, icd11))
        session.close()
        if len(diseases_info) == 0:
            return []
        else:
            result: list = []
            for disease_info in diseases_info:
                icd10_code: str = SqlController._join_icd10_code(disease_info[1])
                result.append({
                    'diseaseId': disease_info[0].id_disease,
                    'diseaseName': disease_info[0].name,
                    'codes': {
                        'icd10': icd10_code,
                        'icd11': disease_info[2].code,
                    },
                    'wikipedia': self.get_wiki_info(disease_info[0].id_disease),
                    'additionalInfo': self.get_additional_info(disease_info[0].id_disease)
                })
            return result

    @staticmethod
    def _join_icd10_code(icd10: Icd10):
        icd10_code: str = ''
        if icd10.category != '':
            icd10_code += icd10.category
            if icd10.details != '':
                icd10_code += '.' + icd10.details
                if icd10.extension != '':
                    icd10_code += '.' + icd10.extension
        return icd10_code

    def get_icd10_info(self, icd10_code: str) -> list:
        id_diseases: list = self.get_disease_id_by_icd10(icd10_code)
        return self.get_disease_info(id_diseases)

    def get_icd11_info(self, icd11_code: str) -> list:
        id_disease: list = self.get_disease_id_by_icd11(icd11_code)
        return self.get_disease_info(id_disease)

    def add_additional_info(self, id_disease: int, info_type: str, author: str, info: str) -> None:
        additional_info = AdditionalInfo(id_disease=id_disease, type=info_type, author=author, info=info)
        session: Session = self.db_session()
        session.merge(additional_info)
        session.commit()
        session.close()

    def modify_additional_info(self, id_info: int, info_type: str, author: str, info: str) -> None:
        session = self.db_session()
        additional_info: AdditionalInfo = session.query(AdditionalInfo) \
            .filter(AdditionalInfo.id_additional_info == id_info)[0]

        additional_info.type = info_type
        additional_info.author = author
        additional_info.info = info

        session.commit()
        session.close()

    def delete_additional_info(self, id_info: int) -> None:
        session = self.db_session()
        additional_info: AdditionalInfo = session.query(AdditionalInfo) \
            .filter(AdditionalInfo.id_additional_info == id_info)[0]

        session.delete(additional_info)

        session.commit()
        session.close()

    def export_to_prolog(self) -> str:
        return ''
