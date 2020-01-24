"""Unit tests for SqlController class"""
import json
from unittest import TestCase

from icd_mapper.classes.db.DbController import DbController
from icd_mapper.classes.db.SqlController import SqlController


class TestSqlController(TestCase):
    db_controller: DbController

    def __init__(self, *args, **kwargs):
        super(TestSqlController, self).__init__(*args, **kwargs)
        with open('../icd_mapper/resources/configuration.json', 'r') as f:
            configuration = json.load(f)

        self.db_controller = SqlController(
            database=configuration['db']['database'],
            host=configuration['db']['host'],
            user=configuration['db']['user'],
            password=configuration['db']['password']
        )

    def test_add_disease_entry(self):
        self.db_controller.add_disease_entry('unit_test')

    def test_get_disease_id(self):
        id_disease: int = self.db_controller.get_disease_id_by_name('unit_test')
        self.assertIsNotNone(id_disease)

    def test_add_wiki_info(self):
        id_disease: int = self.db_controller.get_disease_id_by_name('unit_test')
        self.db_controller.add_wiki_info(id_disease, 'eng', 'eng_title', 'eng_url')
        self.db_controller.add_wiki_info(id_disease, 'pol', 'pol_title', 'pol_url')

    def test_add_icd_codes(self):
        id_disease: int = self.db_controller.get_disease_id_by_name('unit_test')
        self.db_controller.add_icd_codes(id_disease, 'unit.test.in', 'code11')

    def test_get_icd10_info(self):
        disease_info: list = self.db_controller.get_icd10_info('unit.test.in')
        expected_disease_info: dict = {
            "codes": {
                'icd10': 'unit.test.in',
                'icd11': 'code11'
            },
            'diseaseName': 'unit_test',
            'wikipedia': [
                {
                    'lang': 'eng',
                    'title': 'eng_title',
                    'link': 'eng_url'
                }, {
                    'lang': 'pol',
                    'title': 'pol_title',
                    'link': 'pol_url'
                }
            ]
        }
        self.assertDictEqual(expected_disease_info["codes"], disease_info[0]["codes"])
        self.assertEquals(expected_disease_info["diseaseName"], disease_info[0]["diseaseName"])
        self.assertListEqual(expected_disease_info["wikipedia"], disease_info[0]["wikipedia"])

    def test_get_icd11_info(self):
        disease_info: list = self.db_controller.get_icd11_info('code11')
        expected_disease_info: dict = {
            "codes": {
                'icd10': 'unit.test.in',
                'icd11': 'code11'
            },
            'diseaseName': 'unit_test',
            'wikipedia': [
                {
                    'lang': 'eng',
                    'title': 'eng_title',
                    'link': 'eng_url'
                }, {
                    'lang': 'pol',
                    'title': 'pol_title',
                    'link': 'pol_url'
                }
            ]
        }
        self.assertDictEqual(expected_disease_info["codes"], disease_info[0]["codes"])
        self.assertEquals(expected_disease_info["diseaseName"], disease_info[0]["diseaseName"])
        self.assertListEqual(expected_disease_info["wikipedia"], disease_info[0]["wikipedia"])
