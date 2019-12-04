"""Unit tests for MySqlController class"""
import json
from unittest import TestCase

from icd_reader.classes.DbController import DbController
from icd_reader.classes.MySqlController import MySqlController


class TestMySqlController(TestCase):
    db_controller: DbController

    def __init__(self, *args, **kwargs):
        super(TestMySqlController, self).__init__(*args, **kwargs)
        with open('../icd_reader/resources/configuration.json', 'r') as f:
            configuration = json.load(f)

        self.db_controller = MySqlController(
            host=configuration['db-parameters']['host'],
            user=configuration['db-parameters']['user'],
            password=configuration['db-parameters']['password']
        )

    def test_add_disease_entry(self):
        self.db_controller.add_disease_entry('unit_test')

    def test_get_disease_id(self):
        id_disease: int = self.db_controller.get_disease_id('unit_test')
        self.assertIsNotNone(id_disease)

    def test_add_wiki_info(self):
        id_disease: int = self.db_controller.get_disease_id('unit_test')
        self.db_controller.add_wiki_info(id_disease, 'eng_title', 'pol_title', 'eng_url', 'pol_url')

    def test_add_icd_codes(self):
        id_disease: int = self.db_controller.get_disease_id('unit_test')
        self.db_controller.add_icd_codes(id_disease, ['unit', 'test', 'in'], 'code11')
