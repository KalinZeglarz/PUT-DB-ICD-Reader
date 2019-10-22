from unittest import TestCase

from icd_reader.IcdReader import IcdReader


class TestIcdReader(TestCase):
    def test_get_disease_wikipedia_data(self):
        icd_reader: IcdReader = IcdReader('en')
        title, url, pol_url = icd_reader.get_disease_wikipedia_data('E10.3')

        self.assertEqual('Diabetic retinopathy', title)
        self.assertEqual('https://en.wikipedia.org/wiki/Diabetic_retinopathy', url)
        self.assertEqual('https://pl.wikipedia.org/wiki/Retinopatia_cukrzycowa', pol_url)
