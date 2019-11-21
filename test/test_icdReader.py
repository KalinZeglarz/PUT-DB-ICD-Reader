"""Unit tests for IcdReader class"""
from unittest import TestCase

from icd_reader.classes.IcdWikipediaMapper import IcdWikipediaMapper


class TestIcdReader(TestCase):
    def test_get_disease_wikipedia_data(self):
        icd_reader: IcdWikipediaMapper = IcdWikipediaMapper("../icd_reader/resources/codeSpaces.json")
        title, url, pol_url = icd_reader.get_disease_wikipedia_data("E10.3")

        self.assertEqual("Diabetic retinopathy", title)
        self.assertEqual("https://en.wikipedia.org/wiki/Diabetic_retinopathy", url)
        self.assertEqual("https://pl.wikipedia.org/wiki/Retinopatia_cukrzycowa", pol_url)

    def test_get_diseases_wikipedia_data(self):
        icd_reader: IcdWikipediaMapper = IcdWikipediaMapper("../icd_reader/resources/codeSpaces.json")
        diseases: list = ["P14.1", "D51.9", "E10.3", "M07", "L10.0", "L10.3", "L20.9", "P10.4", "ZZ100"]
        data: list = icd_reader.get_diseases_wikipedia_data(diseases)
        self.assertEqual(len(diseases) - 2, len(data))
        for title, url, pol_url in data:
            self.assertTrue(title)
