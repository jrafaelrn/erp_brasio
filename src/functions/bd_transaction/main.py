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

        try:
            id_bank = DATA['id_bank']
        except:
            id_bank = id_generator(6)

        try:
            feedback = insert_transaction(
                date_trx, account, original_description, document, entity_bank, type_trx, value, balance, id_bank)
            feedbacks.append(feedback)

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

@functions_framework.cloud_event
def check(cloud_event):
    
    global line_to_insert
    line_to_insert = None

    logging.info(f"Event ID: {cloud_event['id']}")
    logging.info(f"Event Type: {cloud_event['type']}")

    # 1. Obter os dados brutos do evento (O Envelope do Pub/Sub)
    # O framework já converte o payload do Pub/Sub em um dicionário aqui
    pubsub_message = cloud_event.data

    logging.info(f'Pub/Sub Envelope: {pubsub_message}')

    # Definição padrão
    operation_type = 'insert'
    target_json = None

    try:
        # 2. Verificar se é uma mensagem válida do Pub/Sub
        if 'message' in pubsub_message:
            # O Pub/Sub real aninha os dados dentro de 'message'
            message_body = pubsub_message['message']
        else:
            # Em alguns testes locais ou emulações, os dados podem vir direto
            message_body = pubsub_message

        # 3. Extrair e Decodificar os dados (Payload real)
        if 'data' in message_body:
            data_base64 = message_body['data']
            
            # Decodifica de Base64 para String
            decoded_data = base64.b64decode(data_base64).decode('utf-8')
            logging.info(f'Decoded Data (String): {decoded_data}')

            # Converte a String decodificada para JSON (Lista ou Dict)
            target_json = json.loads(decoded_data)
        else:
            logging.error('Payload Pub/Sub sem o campo "data".')
            return

        # 4. Extrair Atributos (se houver, para definir insert/update)
        attributes = message_body.get('attributes', {})
        operation_type = attributes.get('type', 'insert')
        logging.info(f'Operation Type from Attributes: {operation_type}')

    except Exception as e:
        logging.error(f'FATAL: Falha ao processar mensagem do Pub/Sub: {e}')
        # Em Pub/Sub, não adianta retornar string de erro, pois ninguém recebe.
        # O ideal é logar o erro. Se retornar erro, o Pub/Sub pode tentar reenviar (retry).
        return

    # 5. Executar a lógica de negócio
    try:
        if operation_type == 'insert':
            # Sua função insert já espera a lista (target_json)
            response = insert(target_json)
            logging.info(f'Insert Response: {response}')
        
        elif operation_type == 'update':
            response = update(target_json)
            logging.info(f'Update Response: {response}')

    except Exception as e:
        logging.error(f'Error executing business logic: {e}')

    return 'OK'


# Função principal para rodar localmente em testes
if __name__ == '__main__':
    logging.info('Starting BD Transaction Function locally...')

    # Exemplo de dados para teste local
    test_data = [
        json.dumps({
            "date_trx": "2024-06-01",
            "account": "123456",
            "original_description": "Test Transaction",
            "document": "DOC123",
            "entity_bank": "Test Entity",
            "type_trx": "credit",
            "value": 100.0,
            "balance": 1000.0,
            "id_bank": "BANK001"
        })
    ]

    # Cria o objeto CloudEvent simulado
    attributes = {
        'specversion': '1.0',
        'type': 'insert',
        'source': 'local-test',
        'id': 'test-1'
    }
    data = {"message": {
        "data": base64.b64encode(json.dumps(test_data).encode('utf-8')).decode('utf-8'),
        "attributes": attributes
    }}
    event = CloudEvent(attributes, data)
    check(event)
    
    logging.info('Finished local test of BD Transaction Function.')