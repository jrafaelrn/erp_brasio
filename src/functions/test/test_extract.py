import unittest, sys, os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from bd_update_banks.extract import *


class TestExtraction(unittest.TestCase):

    def test_extract_cpf_cnpj_cliente_fornecedor_from_description(self):
        self.assertEqual(extract_cpf_cnpj_cliente_fornecedor_from_description('RECEBIMENTO PIX SICREDI 12345678910 ABCD'), ('12345678910', 'ABCD'))
        self.assertEqual(extract_cpf_cnpj_cliente_fornecedor_from_description('PAGAMENTO PIX 88111222000199 EMPRESA XYZ'), ('88111222000199', 'EMPRESA XYZ'))
        self.assertEqual(extract_cpf_cnpj_cliente_fornecedor_from_description('COMPRAS NACIONAIS LOJA ABC'), ('', 'LOJA ABC'))
        

    def test_extract_type(self):
        self.assertEqual(extract_type('COMPRAS NACIONAIS SICREDI', 'CARTAO DEB'), 'CARTAO DEB')
        self.assertEqual(extract_type('GETNET DEBITO ELO', 'XYZ'), 'GETNET')
        self.assertEqual(extract_type('CONVENIO', 'DEB AUTOMATICO'), 'DEB AUTOMATICO')
        self.assertEqual(extract_type('DEBITO CONVENIOS ID', '9876'), 'DEB AUTOMATICO')


if __name__ == '__main__':
    unittest.main()
