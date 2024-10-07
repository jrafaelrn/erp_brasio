import json, gspread, io, os, re, bank_sicredi, base64, bank_pagbank
from httplib2 import Credentials
from datetime import datetime
import googlecloudprofiler
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/drive']
files_to_import = []
account_name = None

googlecloudprofiler.start(service='bd-update-banks', service_version='1.0.1', verbose=3)

#################################
#       GOOGLE DRIVE API        #
#################################

def get_api_key():

    api_key = None
    
    try:
        
        try:
            file_service_account = 'key.json'
            actual_folder = os.path.dirname(os.path.abspath(__file__))
            actual_folder = os.path.join(actual_folder, file_service_account)
    
            #Open file
            file = open(actual_folder, 'r')
            file_content_string = file.read()
    
            api_key = json.loads(file_content_string)
            print(f'API KEY Found from File!')
            
        except Exception as e:
            print(f'Error: {e}')            
            service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            api_key = json.loads(service_account)
            print(f'API KEY Found from Environment!')

    except Exception as e:
        print(f'Error: {e}')
        api_key = None    
    
    return api_key


API_KEY = get_api_key()



def get_files_to_import():

    global files_to_import
    print('Searching for files to import...')

    if API_KEY is None:
        print('API KEY not found!')
        return False
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)

    with build('drive', 'v3', credentials=creds) as gdrive:
        
        try:

            response = gdrive.files().list(fields='nextPageToken, ' 'files(id, name)').execute()
            
            for file in response.get('files', []):
                
                name_file = file.get('name')
                #print(f'Analisando File: {name_file}')
                if name_file.find('-import') == -1:
                    continue
                
                id_file = file.get('id')
                path_file = get_file_path(gdrive, id_file)

                file_to_import = {}
                file_to_import['name'] = name_file
                file_to_import['id'] = id_file
                file_to_import['path'] = path_file.upper()
                print(f'File ADD to import: {file_to_import}')
                files_to_import.append(file_to_import)


            print(f'==== Finishid Search --> Files to import: {files_to_import}')
            return True
            
        except Exception as error:
            print(F'An error occurred: {error}')
            return False




def get_file(file_id):
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)

    with build('drive', 'v3', credentials=creds) as gdrive:
        
        try:

            request = gdrive.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(F'Download {int(status.progress() * 100)}%')

        except HttpError as error:
            print(F'An error occurred: {error}')
            print('Probably any file is found.')
            return None

        return file.getvalue()



def get_file_path(gdrive, file_id):

    response = gdrive.files().get(fileId=file_id, fields='id, name, parents').execute()
    path_result = ''

    parent = response.get('parents')
    if parent:
        while True:
            folder = gdrive.files().get(fileId=parent[0], fields='id, name, parents').execute()
            parent = folder.get('parents')
            if parent is None:
                break
            path_result = folder.get('name') + '/' + path_result

    
    print(f'Path: {path_result}')
    return path_result



def rename_file(file_id, old_name_file):

    new_name_file = old_name_file.replace('-import', '-ok')
    #print(f'New name file: {new_name_file}')
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)

    with build('drive', 'v3', credentials=creds) as gdrive:
        
        try:

            file_metadata = {
                'name': new_name_file
            }

            gdrive.files().update(fileId=file_id, body=file_metadata).execute()
            return True

        except HttpError as error:
            print(F'An error occurred: {error}')
            return False



def check_if_file_exists(path_filter, name_filter):

    global files_to_import

    for file in files_to_import:
        if file['path'].find(path_filter.upper()) != -1 and file['name'] == name_filter:
            return True, file['id']

    return False, None



#################################
#      PRINCIPAL - METHOD       #
#################################

def update_bd():

    get_files_to_import()
    global files_to_import
    print(f'.... Files to import...: {files_to_import}')

    for file_to_import in files_to_import:

        print(f'.........Importing file...: {file_to_import}')

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
    
    print(f'Updating BD from Sicredi: {file_to_import}')

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
        print(f'Folder not CHECK_FOLDER: {file_path}')
        return None, None, None, None
    
    import_card = False

    file_excel = get_file(file_id)

    if file_excel is None:
        print('No file found!')
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
            return None, None, None, None


    # Rename file
    if rename_file(file_id, file_name):
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
    if rename_file(file_id_card, card_name_file_filter):
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
    if rename_file(file_id, file_name):
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

def check(event, context):

    if type(event) != str:
        payload = base64.b64decode(event['data']).decode('utf-8')
    else:
        payload = event

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
    update_bd()
    print('Update BD!')