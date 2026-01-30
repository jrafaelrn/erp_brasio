import base64
import functions_framework
import googlecloudprofiler
import gspread
import json
import os
import logging
import pandas as pd
import random
import string
import time
import sys


from cloudevents.http import CloudEvent


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    force=True
)

logger = logging.getLogger()


class LineNotFoundError(Exception):
    pass


def get_api_key():
    
    api_key = None
    logger.info('Getting API KEY...')
    
    try:
        
        try:
            file_service_account = 'key.json'
            actual_folder = os.path.dirname(os.path.abspath(__file__))
            actual_folder = os.path.join(actual_folder, file_service_account)
    
            #Open file
            file = open(actual_folder, 'r')
            file_content_string = file.read()
    
            api_key = json.loads(file_content_string)
            logger.info('API KEY Found from File!')
            
        except Exception as e:
            logger.error(f'Error: {e}')            
            service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            api_key = json.loads(service_account)
            logger.info('API KEY Found from Environment!')

    except Exception as e:
        logger.error(f'Error: {e}')
        api_key = None    
    
    return api_key



def open_bd_bank():

    API_KEY = get_api_key()
    sa = gspread.service_account_from_dict(API_KEY)
    bd = sa.open("bd_bot")
    bd_sheet = bd.worksheet('bank')

    if bd_sheet is None:
        raise Exception('Worksheet bank not found in bd_bot spreadsheet!')

    return bd_sheet


line_to_insert = None
bd = None
bd_pd = None


def insert_transaction(date_trx, account, original_description, document, entity_bank, type_trx, value, balance, id_bank):

    global line_to_insert
    global bd
    global bd_pd

    logging.info(
        f'Starting insert transaction - Date: {date_trx} - Account: {account} - Original Description: {original_description} - Document: {document} - Entity Bank: {entity_bank} - Type Trx: {type_trx} - Value: {value} - Balance: {balance}')
    entity_bank = entity_bank.strip()

    if line_to_insert is None:

        line_to_insert = 0
        bd = open_bd_bank()
        bd_pd = pd.DataFrame(bd.get_all_records(
            value_render_option='UNFORMATTED_VALUE'))

        # loop to find the first empty line
        for row in bd_pd.iterrows():

            id_row = row[1]['ID_BANCO']

            if id_row != "":
                line_to_insert += 1

        line_to_insert += 2

    logging.info(f'ID to add to Bank: {id_bank} - LINE: {line_to_insert}')
    if line_to_insert == 0:
        raise LineNotFoundError('Error to find line to insert!')

    # Append new row
    row = [id_bank, date_trx, account, original_description,
           document, entity_bank, type_trx, value, balance]

    # Save BD
    for col in range(ord('a'), ord('i') + 1):
        coluna = chr(col)
        conteudo = [[row[col - ord('a')]]]

        if conteudo == '':
            continue

        print(f'Coluna: {coluna} - Conteudo: {conteudo}')
        bd.update(f'{coluna}{line_to_insert}', conteudo)

    line_to_insert += 1
    msg = f'Lancamento inserido!! ID: {id_bank} - Data: {date_trx} - Conta: {account} - Descrição: {original_description} - Documento: {document} - Entidade: {entity_bank} - Tipo: {type_trx} - Valor: {value} - Saldo: {balance}'
    print(msg)
    time.sleep(0.1)
    return msg


def update_transaction(id, category_erp=None, entity_erp=None, status_erp=None, description_erp=None):

    bd = open_bd_bank()
    line = bd.find(f'{id}').row

    # Update row
    if category_erp is not None:
        category_erp = category_erp.strip()
        category_erp = " ".join(category_erp.split())
        category_columns = bd.find('CATEGORY_ERP').col
        cel = f'{chr(category_columns + ord("a") - 1)}{line}'
        bd.update(cel, category_erp)

    if entity_erp is not None:
        entity_erp = entity_erp.strip()
        entity_erp = " ".join(entity_erp.split())
        entity_column = bd.find('ENTITY_ERP').col
        cel = f'{chr(entity_column + ord("a") - 1)}{line}'
        bd.update(cel, entity_erp)

    if status_erp is not None:
        status_erp = status_erp.strip()
        status_erp_column = bd.find('STATUS_ERP').col
        cel = f'{chr(status_erp_column + ord("a") - 1)}{line}'
        bd.update(cel, status_erp)

    if description_erp is not None:
        description_erp = description_erp.strip()
        description_erp = " ".join(description_erp.split())
        description_erp_column = bd.find('DESCRIPTION_ERP').col
        cel = f'{chr(description_erp_column + ord("a") - 1)}{line}'
        bd.update(cel, description_erp)

    coluna_classificado_bot = bd.find('BOT_CLASSIFICATION').col
    celula = f'{chr(coluna_classificado_bot + ord("a") - 1)}{line}'
    bd.update(celula, '1')

    msg = f'Lancamento {id} atualizado!! - Grupo: {category_erp} - Cliente/Fornecedor: {entity_erp} - Status ERP: {status_erp} - Descrição ERP: {description_erp}'
    print(msg)
    return msg


def insert(data):

    # Transfor to json
    try:
        ARRAY_DATA = json.loads(data)

    except Exception as e:
        print(f'Error when parse JSON: {e}')

        # Se ARRAY_DATA for do tipo 'list',
        if type(data) == list:
            ARRAY_DATA = data
            logging.info(
                f'ARRAY_DATA: {ARRAY_DATA} -- Type: {type(ARRAY_DATA)}')

        else:
            return f'FATAL ERROR when parse JSON: {e}'

    feedbacks = []

    for DATA in ARRAY_DATA:

        DATA = json.loads(DATA)

        date_trx = DATA['date_trx']
        account = DATA['account']
        original_description = DATA['original_description']
        document = DATA['document']
        entity_bank = DATA['entity_bank']
        type_trx = DATA['type_trx']
        value = DATA['value']
        balance = DATA['balance']
        id_bank = DATA.get('id_bank', id_generator(6))

        try:
            feedback = insert_transaction(
                date_trx, account, original_description, document, entity_bank, type_trx, value, balance, id_bank)
            feedbacks.append(feedback)
            
        except LineNotFoundError as e:
            logging.error(feedback)
            raise e

        except Exception as e:
            feedback = f'Error when inserting transaction: {e}'
            logging.error(feedback)
            feedbacks.append(feedback)

    return feedbacks


def update(data):

    id = data['id']
    category_erp = data['category_erp']
    entity_erp = data['entity_erp']
    status_erp = data['status_erp']
    description_erp = data['description_erp']

    feedback = ''

    try:
        feedback = update_transaction(
            id, category_erp, entity_erp, status_erp, description_erp)
    except Exception as e:
        feedback = f'Error when updating transaction: {e}'
        logging.error(feedback)

    return feedback


def id_generator(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


#################################
#   Call from Cloud Functions   #
#################################

@functions_framework.http    
def check(request):

    global line_to_insert
    line_to_insert = None

    request_json = request.get_json(silent=True)
    parameters = request.args
    print(f'Request JSON: {request_json}')
    print(f'Parameters: {parameters}')
    
    if parameters['type'] == 'insert':
        response = insert(request_json)
        response = json.dumps(response)
    
    elif parameters['type'] == 'update':
        response = update(request_json)

    else:
        response = '{}'
    
    print(f'Response: {response}')
    return response



if __name__ == '__main__':    
    data = ['{"date_trx": "26/01/2026", "account": "SICREDI-BRUNA", "original_description": "SICREDI ANTECIPACAO VISA | SICREDI | 0001-00", "document": "", "entity_bank": "", "type_trx": "OUTROS", "value": 601.51, "balance": 17522.34}', '{"date_trx": "26/01/2026", "account": "SICREDI-BRUNA", "original_description": "RECEBIMENTO PIX 05323537000106 ADEGA BRUNHOLI LT", "document": "5323537000106", "entity_bank": "ADEGA BRUNHOLI LT", "type_trx": "PIX_CRED", "value": 115.8, "balance": 17638.14}', '{"date_trx": "26/01/2026", "account": "SICREDI-BRUNA", "original_description": "PAGAMENTO PIX 28067799873 M\\u00d4NICA MARIANA PERANDI", "document": "28067799873", "entity_bank": "M\\u00d4NICA MARIANA PERANDI", "type_trx": "PIX_DEB", "value": -5140, "balance": 12498.14}', '{"date_trx": "26/01/2026", "account": "SICREDI-BRUNA", "original_description": "PAGAMENTO PIX 00394460005887 RECEITA FEDERAL", "document": "394460005887", "entity_bank": "RECEITA FEDERAL", "type_trx": "PIX_DEB", "value": -340.57, "balance": 12157.57}', '{"date_trx": "26/01/2026", "account": "SICREDI-BRUNA", "original_description": "PAGAMENTO PIX 00394460005887 RECEITA FEDERAL", "document": "394460005887", "entity_bank": "RECEITA FEDERAL", "type_trx": "PIX_DEB", "value": -376.96, "balance": 11780.61}', '{"date_trx": "26/01/2026", "account": "SICREDI-BRUNA", "original_description": "PAGAMENTO PIX 43188608845 ARIANE FERREIRA MENDES", "document": "43188608845", "entity_bank": "ARIANE FERREIRA MENDES", "type_trx": "PIX_DEB", "value": -284, "balance": 11496.61}']
    request_json = json.dumps(data)
    
    # call insert
    print(f'Request JSON: {request_json}')
    response = insert(request_json)
    