"""Unit tests for IcdReader class"""
from unittest import TestCase

from icd_reader.classes.IcdWikipediaMapper import IcdWikipediaMapper


class TestIcdReader(TestCase):
    def test_get_disease_wikipedia_data(self):
        wikipedia_mapper: IcdWikipediaMapper = IcdWikipediaMapper("../icd_reader/resources/codeSpaces.json")
        language, title, url = wikipedia_mapper.get_disease_wikipedia_data("E10.3")[0]

        self.assertEqual("en", language)
        self.assertEqual("Diabetic retinopathy", title)
        self.assertEqual("https://en.wikipedia.org/wiki/Diabetic_retinopathy", url)

    def test_get_diseases_wikipedia_data(self):
        wikipedia_mapper: IcdWikipediaMapper = IcdWikipediaMapper("../icd_reader/resources/codeSpaces.json")
        diseases: list = ["P14.1", "D51.9", "E10.3", "M07", "L10.0", "L10.3", "L20.9", "P10.4", "ZZ100"]
        result: list = wikipedia_mapper.get_diseases_wikipedia_data(diseases)
        self.assertEqual(len(diseases) - 2, len(result))
        for data in result:
            language, title, url = data[0]
            self.assertEqual("en", language)
            self.assertTrue(title)
