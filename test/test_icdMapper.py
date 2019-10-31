from unittest import TestCase

from icd_reader.icd_mapper.IcdMapper import IcdMapper


class TestIcdMapper(TestCase):
    def test_icd_10_to_icd_11(self):
        CLIENT_ID: str = '74009638-34b6-4960-b9f0-2ed5acd08e71_fa0bcb22-3fa7-4149-8427-82891d884572'
        CLIENT_SECRET: str = 'qfRSgmvnd7b6NBvYB3NAs0UwIPEU3pXAiFQODGMFhb8='

        icd_mapper: IcdMapper = IcdMapper(CLIENT_ID, CLIENT_SECRET)
        icd_10_code: str = "H02.2"
        icd_11_code: str = icd_mapper.icd_10_to_icd_11(icd_10_code)
        self.assertEqual('9A03.40', icd_11_code)
