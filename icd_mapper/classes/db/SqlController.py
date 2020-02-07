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

    def check_connection(self) -> bool:
        from sqlalchemy.exc import DatabaseError
        try:
            connection = self.engine.connect()
            connection.close()
        except DatabaseError:
            return False
        return True

    def add_disease_entry(self, name: str) -> None:
        session: Session = self.db_session()
        disease: Disease = session.query(Disease).filter(Disease.name == name).first()
        if not disease:
            disease = Disease(name=name.lower())
            session.add(disease)
        elif disease.name != name.lower():
            disease.name = name.lower()
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
        session = self.db_session()
        icd10_list: List[Icd10] = session.query(Icd10.id_disease) \
            .filter(Icd10.code.startswith(icd10)).all()
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
        wiki: Wiki = session.query(Wiki) \
            .filter(Wiki.id_disease == id_disease, Wiki.language == language).first()
        if not wiki:
            wiki = Wiki(id_disease=id_disease, language=language, title=title.lower(), link=link)
            session.add(wiki)
        elif wiki.title != title.lower() or wiki.link != link:
            wiki.title = title.lower()
            wiki.link = link
        session.commit()
        session.close()

    def add_icd_codes(self, id_disease: int, icd10_code: str, icd11_code: str):
        icd10 = Icd10(id_disease=id_disease, code=icd10_code.lower())
        icd11 = Icd11(id_disease=id_disease, code=icd11_code.lower())

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
                .filter(Disease.id_disease == id_disease).first()
            icd10: Icd10 = session.query(Icd10) \
                .filter(Icd10.id_disease == id_disease).first()
            icd11: Icd11 = session.query(Icd11) \
                .filter(Icd11.id_disease == id_disease).first()
            diseases_info.append((disease, icd10, icd11))
        session.close()
        if not diseases_info:
            return []
        else:
            result: list = []
            for disease_info in diseases_info:
                if disease_info[0] is None:
                    continue
                result.append({
                    'diseaseId': disease_info[0].id_disease,
                    'diseaseName': disease_info[0].name,
                    'codes': {
                        'icd10': disease_info[1].code,
                        'icd11': disease_info[2].code,
                    },
                    'relations': self.get_disease_relations(disease_info[0].id_disease),
                    'wikipedia': self.get_wiki_info(disease_info[0].id_disease),
                    'additionalInfo': self.get_additional_info(disease_info[0].id_disease)
                })
            return result

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

    def add_disease_relation(self, id_disease_1: int, id_disease_2: int, rel_type: str) -> None:
        session: Session = self.db_session()
        relation: DiseaseRel = session.query(DiseaseRel) \
            .filter(DiseaseRel.id_disease_1 == id_disease_1, DiseaseRel.id_disease_2 == id_disease_2).first()
        if not relation:
            disease_rel = DiseaseRel(id_disease_1=id_disease_1, id_disease_2=id_disease_2, rel_type=rel_type)
            session.add(disease_rel)
        elif relation.rel_type != rel_type:
            relation.rel_type = rel_type
        session.commit()
        session.close()

    def get_disease_relations(self, id_disease_1: int) -> list:
        session: Session = self.db_session()
        disease_rels: List[DiseaseRel] = session.query(DiseaseRel) \
            .filter(DiseaseRel.id_disease_2 == id_disease_1).all()
        session.close()
        result: list = []
        for disease_rel in disease_rels:
            result.append({
                'id_disease': disease_rel.id_disease_1,
                'type': disease_rel.rel_type
            })
        return result

    def search_diseases(self, sentence: str) -> list:
        session: Session = self.db_session()
        id_diseases_1: List[Disease] = session.query(Disease.id_disease) \
            .filter(Disease.name.contains(sentence.lower())) \
            .all()
        session.close()
        id_diseases_2: List[Wiki] = session.query(Wiki.id_disease) \
            .filter(Wiki.title.contains(sentence.lower())) \
            .all()
        session.close()

        id_diseases: set = set()
        for item in id_diseases_1:
            id_diseases.add(item.id_disease)
        for item in id_diseases_2:
            id_diseases.add(item.id_disease)

        return self.get_disease_info(list(id_diseases))

    def export_to_prolog(self) -> str:
        return ''
