import json, gspread, os
import pandas as pd


def get_api_key():

    api_key = None
    
    try:
        
        try:
            file_service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    
            #Open file
            file = open(file_service_account, 'r')
            file_content_string = file.read()
    
            api_key = json.loads(file_content_string)
            
        except Exception as e:
            print(f'Error: {e}')            
            service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            api_key = json.loads(service_account)

    except Exception as e:
        print(f'Error: {e}')
        api_key = None    
    
    return api_key



def open_bd_bank():

    API_KEY = get_api_key()
    sa = gspread.service_account_from_dict(API_KEY)
    bd = sa.open("bd_bot")
    bd_sheet = bd.worksheet('bank')
    return bd_sheet


def insert_transaction(date_trx, account, original_description, document, entity_bank, type_trx, value, balance):

    print(f'Starting insert transaction - Date: {date_trx} - Account: {account} - Original Description: {original_description} - Document: {document} - Entity Bank: {entity_bank} - Type Trx: {type_trx} - Value: {value} - Balance: {balance}')

    entity_bank = entity_bank.strip()
    bd = open_bd_bank()
    bd_pd = pd.DataFrame(bd.get_all_records(value_render_option='UNFORMATTED_VALUE'))

    # loop to check if the transaction already exists
    for row in bd_pd.iterrows():

        #print(f'Row: {row}')
        date_row = row[1]['DATA']
        account_bank = row[1]['CONTA']
        description = row[1]['DESCRICAO_ORIGINAL']
        valor = row[1]['VALOR']
        saldo = row[1]['SALDO']

        #print(f'Comparing - Date: {date_trx} x {date_row} - Account: {account} x {account_bank} - Description: {original_description} x {description} - Value: {float(value)} x {float(valor)} - Balance: {float(balance)} x {float(saldo)}')

        if date_row == date_trx and account_bank == account and description == original_description and float(valor) == float(value) and float(saldo) == float(balance):
            msg = f'Lancamento já existe no banco de dados'
            print(msg)
            return msg

    
    # Get MAX_ID from column ID
    max_id = bd_pd['ID'].max()
    id = int(max_id) + 1
    print(f'ID: {id}')

    # Append new row
    row = [id, date_trx, account, original_description, document, entity_bank, type_trx, value, balance]

    #Save BD
    line = len(bd_pd.index) + 2
    for col in range(ord('a'), ord('i') + 1): 
        coluna = chr(col)
        conteudo = row[col - ord('a')]
        
        if conteudo == '':
            continue
        
        bd.update(f'{coluna}{line}', conteudo)


    msg = f'Lancamento inserido!! ID: {id} - Data: {date_trx} - Conta: {account} - Descrição: {original_description} - Documento: {document} - Entidade: {entity_bank} - Tipo: {type_trx} - Valor: {value} - Saldo: {balance}'
    print(msg) 
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

    #Transfor to json
    try:
        DATA = json.loads(data)
    except Exception as e:
        print(f'Error when parse JSON: {e}')
        DATA = data

    date_trx = DATA['date_trx']
    account = DATA['account']
    original_description = DATA['original_description']
    document = DATA['document']
    entity_bank = DATA['entity_bank']
    type_trx = DATA['type_trx']
    value = DATA['value']
    balance = DATA['balance']

    feedback = ''

    try:
        feedback = insert_transaction(date_trx, account, original_description, document, entity_bank, type_trx, value, balance)
    except Exception as e:
        feedback = f'Error when inserting transaction: {e}' 
        print(feedback)

    return feedback



def update(data):

    id = data['id']
    category_erp = data['category_erp']
    entity_erp = data['entity_erp']
    status_erp = data['status_erp']
    description_erp = data['description_erp']

    feedback = ''

    try:
        feedback = update_transaction(id, category_erp, entity_erp, status_erp, description_erp)
    except Exception as e:
        feedback = f'Error when updating transaction: {e}'
        print(feedback)

    return feedback



#################################
#   Call from Cloud Functions   #
#################################

def check(request):

    request_json = request.get_json(silent=True)
    parameters = request.args
    print(f'Request JSON: {request_json}')
    print(f'Parameters: {parameters}')
    
    if parameters['type'] == 'insert':
        response = insert(request_json)
    
    elif parameters['type'] == 'update':
        response = update(request_json)

    else:
        response = '{}'
    
    print(f'Response: {response}')
    return response