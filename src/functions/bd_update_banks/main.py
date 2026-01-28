import bank_pagbank
import bank_sicredi
import base64
import io
import logging
import re
import pandas as pd
import functions_framework


from httplib2 import Credentials
from datetime import datetime
from cloudevents.http import CloudEvent
from google_drive import *



#################################
#      PRINCIPAL - METHOD       #
#################################

def update_bd():

    get_files_to_import()
    global files_to_import
    logging.info(f'.... Files to import...: {files_to_import}')

    for file_to_import in files_to_import:

        logging.info(f'.........Importing file...: {file_to_import}')

        # Check if credit file to avoid start with 
        if file_to_import.get('path').upper().find('CARTAO-CSV') != -1:
            continue
        
        if file_to_import.get('path').upper().find('SICREDI') != -1:
            update_bd_from_sicredi(file_to_import)
            
        if file_to_import.get('path').upper().find('PAGBANK') != -1:
            update_bd_from_pagbank(file_to_import)

        return
            

##########################################
#               SICREDI                  #
##########################################

def update_bd_from_sicredi(file_to_import):
    
    logging.info(f'Updating BD from Sicredi: {file_to_import}')

    balance_card, date_payment_card, file_id_card, card_name_file_filter = update_bd_from_sicredi_account(file_to_import)

    # Import CARD SICREDI
    if balance_card is not None:
        update_bd_from_sicredi_card(file_id_card, balance_card, date_payment_card, card_name_file_filter)



def update_bd_from_sicredi_account(file_to_import):
    
    global account_name

    # Import BANK SICREDI
    file_name = file_to_import['name']
    file_id = file_to_import['id']
    file_path = file_to_import['path']
    account_name = str(file_path.split('/')[1]).upper()

    if not check_folder_path(file_path):
        logging.error(f'Folder not CHECK_FOLDER: {file_path}')
        return None, None, None, None
    
    import_card = False

    file_excel = get_file(file_id)

    if file_excel is None:
        logging.error('No file found!')
        return None, None, None, None
            
    df = pd.read_excel(io.BytesIO(file_excel))
    import_card, balance_card, date_payment_card = bank_sicredi.import_extrato_sicredi(df, account_name)
    card_name_file_filter = None
    file_id_card = None

    # Check if card file exists
    if import_card:
        
        print(f'Checking if card file exists...')

        card_path_file_filter = f'{account_name}/CARTAO-CSV/'
        card_name_file_filter = datetime.strptime(date_payment_card, '%d/%m/%Y').strftime('%Y-%m') + '-import.xls'
        file_name_card, file_id_card = check_if_file_exists(card_path_file_filter, card_name_file_filter)

        if file_name_card is False:
            print(f'Card file not found! -- Card Path File Filter: {card_path_file_filter} -- Card Name File Filter: {card_name_file_filter}')
            rename_file(file_id, file_name, 'error')
            return None, None, None, None


    # Rename file
    if rename_file(file_id, file_name, 'ok'):
        print('File renamed!')
    else:
        print('ERROR - File not renamed!')   

    return balance_card, date_payment_card, file_id_card, card_name_file_filter
        


def update_bd_from_sicredi_card(file_id_card, balance_card, date_payment_card, card_name_file_filter):
    
    print(f'Starting update BD from Sicredi Card...\nFile Card ID: {file_id_card}\nBalance Card: {balance_card}\nDate Payment Card: {date_payment_card}\nCard Name File Filter: {card_name_file_filter}')

    global account_name
    
    file_excel = get_file(file_id_card)

    if file_excel is None:
        print('No file found!')
        return
    
    df = pd.read_excel(io.BytesIO(file_excel))            
    bank_sicredi.import_card_sicredi(df, balance_card, date_payment_card, account_name)

    # Rename file
    if rename_file(file_id_card, card_name_file_filter, 'ok'):
        print('File renamed!')
    else:
        print('ERROR - File not renamed!')  




##########################################
#               PAGBANK                  #
##########################################

def update_bd_from_pagbank(file_to_import):
    
    print(f'...Updating BD from PagBank...: {file_to_import}')

    # Import BANK PAGBANK
    file_name = file_to_import['name']
    file_id = file_to_import['id']
    file_path = file_to_import['path']
    
    if not check_folder_path(file_path):
        print(f'Folder not pass CHECK_FOLDER: {file_path}')
        return
    
    file_excel = get_file(file_id)

    if file_excel is None:
        print('No file found!')
        return

    conta = file_path.split('/')[1].upper()
    
    df = pd.read_csv(io.BytesIO(file_excel), sep=';')
    bank_pagbank.import_extrato_pagbank(df, conta)

    # Rename file
    if rename_file(file_id, file_name, 'ok'):
        print('File renamed!')
    else:
        print('ERROR - File not renamed!') 
        
        
        
##########################################
#               FUNCTIONS                #
##########################################

def check_folder_path(folder_to_check: str):
    
    file_path_filter = ['Sicredi/Conta/','Sicredi-Bruna/Conta-CSV/', 'Sicredi-Bruna-0002/Conta-CSV/'] 
    
    for path_filter in file_path_filter:
        if folder_to_check.upper().find(path_filter.upper()) != -1:
            return True
        
        
    file_path_filter = r"(.)*PagBank(.)*/Conta/"
    conta_filter = r"Extratos Bancarios/(.*)/Conta"

    filter = re.match(file_path_filter, folder_to_check)
    if filter:
        return True
        
    return False



#################################
#   Call from Cloud Functions   #
#################################

@functions_framework.cloud_event
def check(cloud_event: CloudEvent):

    print('Starting BD Update Banks...')
    
    payload = cloud_event.data
    response = None
    print(f'Payload: {payload}')
    
    try:
        update_bd()
        response = {"return": "ok"}
    except:
        response = {"return": "error"}

    print(f'Response: {response}')
    return response


if __name__ == '__main__':
    #print('Starting BD Update Banks...')
    update_bd()
    print('Update BD!')