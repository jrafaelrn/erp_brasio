import json, gspread, os
import pandas as pd



def open_bd_bank():

    service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    service_account_dict = json.loads(service_account)
    sa = gspread.service_account_from_dict(service_account_dict)
    bd = sa.open("bd_bot")
    bd_sheet = bd.worksheet('bank')
    bd_pd = pd.DataFrame(bd_sheet.get_all_records())
    return bd_pd


def insert_transaction(date_trx, account, original_description, document, entity, type_trx, value, balance):

    entity = entity.strip()
    date_trx = date_trx.strftime('%d/%m/%Y')
    bd = open_bd_bank()

    # Get Max Id fro last row
    max_id = bd.col_values(1)[-1]
    id = int(max_id) + 1

    # Append new row
    row = [id, date_trx, account, original_description, document, entity, type_trx, value, balance]

    #Save BD
    line = len(bd.col_values(1)) + 1
    for col in range(ord('a'), ord('i') + 1): 
        coluna = chr(col)
        conteudo = row[col - ord('a')]
        
        if conteudo == '':
            continue
        
        bd.update(f'{coluna}{line}', conteudo)


    msg = f'Lancamento inserido!! ID: {id} - Data: {date_trx} - Conta: {account} - Descrição: {original_description} - Documento: {document} - Entidade: {entity} - Tipo: {type_trx} - Valor: {value} - Saldo: {balance}'
    print(msg) 
    return msg





def update_transaction(id, category=None, entity=None, status_erp=None, description_erp=None):
    
    bd = open_bd_bank()
    line = bd.find(f'{id}').row

    # Update row
    if category is not None:
        category = category.strip()
        category = " ".join(category.split())
        category_columns = bd.find('CATEGORY_ERP').col
        cel = f'{chr(category_columns + ord("a") - 1)}{line}'
        bd.update(cel, category)

    if entity is not None:
        entity = entity.strip()
        entity = " ".join(entity.split())
        entity_column = bd.find('CLIENTE/FORNECEDOR_CONSUMER').col
        cel = f'{chr(entity_column + ord("a") - 1)}{line}'
        bd.update(cel, entity)

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

    msg = f'Lancamento {id} atualizado!! - Grupo: {category} - Cliente/Fornecedor: {entity} - Status ERP: {status_erp} - Descrição ERP: {description_erp}'
    print(msg)
    return msg



def insert(data):

    date_trx = data['date_trx']
    account = data['account']
    original_description = data['original_description']
    document = data['document']
    entity = data['entity']
    type_trx = data['type_trx']
    value = data['value']
    balance = data['balance']

    feedback = ''

    try:
        feedback = insert_transaction(date_trx, account, original_description, document, entity, type_trx, value, balance)
    except Exception as e:
        feedback = f'Error when inserting transaction: {e}' 
        print(feedback)

    return feedback



def update(data):

    id = data['id']
    category = data['category']
    entity = data['entity']
    status_erp = data['status_erp']
    description_erp = data['description_erp']

    feedback = ''

    try:
        feedback = update_transaction(id, category, entity, status_erp, description_erp)
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