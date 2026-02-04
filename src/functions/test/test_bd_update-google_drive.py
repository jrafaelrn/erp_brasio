import unittest, sys, os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from bd_update_banks.google_drive import get_bank_name_from_path

class TestGetBankNameFromPath(unittest.TestCase):
    
    def test_only_sicredi(self):
        path_file = '/some/path/SICREDI/account-import.csv'
        bank_name = get_bank_name_from_path(path_file)
        self.assertEqual(bank_name, 'SICREDI')
        
    def test_sicredi_othername(self):
        path_file = '/some/path/SICREDI-ABC/2020/account-import.csv'
        bank_name = get_bank_name_from_path(path_file)
        self.assertEqual(bank_name, 'SICREDI-ABC')
        
    def test_sicredi_othername_number(self):
        path_file = '/SICREDI-ABC-123/Conta-CSV/2020/account-import.csv'
        bank_name = get_bank_name_from_path(path_file)
        self.assertEqual(bank_name, 'SICREDI-ABC-123')

