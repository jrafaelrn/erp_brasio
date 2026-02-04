from datetime import datetime
from dataclasses import dataclass

from bank import Bank

import bd
import extract
import json
import logging
import re
import requests
import time
import pandas as pd


@dataclass
class BankPagbank(Bank):

    def import_extrato_pagbank(self, extrato_file, conta):

        logging.info(f'Importing PagBank file: {extrato_file}')     
        
        for line in extrato_file.iterrows():        
            
            cod_transacao = str(line[1][0])
            data = datetime.strptime(line[1][1], '%d/%m/%Y')
            tipo_old = str(line[1][2])
            descricao = str(f'{tipo_old} - {line[1][3]}')
            doc, nome = extract.extract_cpf_cnpj_cliente_fornecedor_from_description(descricao)
            logging.info(f'DOC: {doc} - NOME: {nome}')
            tipo = str(extract.extract_type(descricao, tipo_old))
            valor = float(line[1][4].replace(',', '.'))
            conta = str(conta.upper())
            descricao = descricao.upper()

            DATA = {}
            DATA['date_trx'] = line[1][1]
            DATA['account'] = conta
            DATA['original_description'] = descricao
            DATA['document'] = doc
            DATA['entity_bank'] = nome
            DATA['type_trx'] = tipo
            DATA['value'] = valor
            DATA['balance'] = 0
            DATA['id_bank'] = cod_transacao

            DATA_JSON = json.dumps(DATA)

            bd.insert(DATA_JSON)

            time.sleep(1.5)



    # Day format = YYYY-MM-DD
    def api_import(self, day):

        page_number = 1
        page_size = 1000
        edi_version = 2.01
        movement_type = [1, 2, 3]
        
        for mov_type in movement_type:
        
            url = f"https://edi.api.pagseguro.com.br/edi/v1/{edi_version}/movimentos?dataMovimento={day}&pageNumber={page_number}&pageSize={page_size}&tipoMovimento={mov_type}"
            headers = {"Accept": "application/json"}

            response = requests.get(url, headers=headers)

            logging.info(f'GET: {url}')
            logging.info(f'RESPONSE: {response.text}')



    def update_bd_from_pagbank(self, file_to_import):
        
        logging.info(f'...Updating BD from PagBank...: {file_to_import}')

        # Import BANK PAGBANK
        file_name = file_to_import['name']
        file_id = file_to_import['id']
        file_path = file_to_import['path']
        
        if not check_folder_path(file_path):
            logging.error(f'Folder not pass CHECK_FOLDER: {file_path}')
            return
        
        file_excel = get_file(file_id)

        if file_excel is None:
            logging.error('No file found!')
            return

        conta = file_path.split('/')[1].upper()
        
        df = pd.read_csv(io.BytesIO(file_excel), sep=';')
        self.import_extrato_pagbank(df, conta)

        # Rename file
        if rename_file(file_id, file_name, 'ok'):
            logging.info('File renamed!')
        else:
            logging.error('ERROR - File not renamed!') 
            



    #day = '2022-08-20'
    #api_import(day)
