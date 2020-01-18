from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class Disease(Base):
    __tablename__ = 'DISEASES'

    id_disease = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<Disease(NAME='{}')>".format(self.name)


class Icd10(Base):
    __tablename__ = 'ICD_10'

    id_disease = Column(Integer, ForeignKey("DISEASES.id_disease"), primary_key=True, nullable=False)
    category = Column(String)
    details = Column(String)
    extension = Column(String)

    def __repr__(self):
        return "<Icd10(CATEGORY='{}', DETAILS='{}', EXTENSION='{}')>".format(self.category, self.details,
                                                                             self.extension)


class Icd11(Base):
    __tablename__ = 'ICD_11'

    id_disease = Column(Integer, ForeignKey("DISEASES.id_disease"), primary_key=True, nullable=False)
    code = Column(String)

    def __repr__(self):
        return "<Icd11(CODE='{}')>".format(self.code)


class Wiki(Base):
    __tablename__ = 'WIKI'

    id_disease = Column(Integer, ForeignKey("DISEASES.id_disease"), nullable=False)
    language = Column(String)
    title = Column(String)
    link = Column(String, primary_key=True)

    def __repr__(self):
        return "<Icd10(LANGUAGE='{}', TITLE='{}', LINK='{}')>".format(self.language, self.title, self.link)


class AdditionalInfo(Base):
    __tablename__ = 'ADDITIONAL_INFO'

    id_disease = Column(Integer, ForeignKey("DISEASES.id_disease"), nullable=False)
    id_additional_info = Column(Integer, primary_key=True, nullable=False)
    type = Column(String)
    author = Column(String)
    info = Column(String)

    def __repr__(self):
        return "<Icd10(TYPE='{}', AUTHOR='{}', INFO='{}')>".format(self.type, self.author, self.info)
