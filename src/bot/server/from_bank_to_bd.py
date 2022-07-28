import from_bank_sicredi
from datetime import datetime
from httplib2 import Credentials
import os, json, io, time
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_api_key():

    api_key = None
    
    try:
        
        try:
            file_service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    
            #Open file
            file = open(file_service_account, 'r')
            file_content_string = file.read()
    
            api_key = json.loads(file_content_string)
            print(f'API KEY Found!')
            
        except Exception as e:
            print(f'Error: {e}')            
            service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            api_key = json.loads(service_account)
            print(f'API KEY Found!')

    except Exception as e:
        print(f'Error: {e}')
        api_key = None    
    
    return api_key


API_KEY = get_api_key()






def download_all(downloads_day, import_bd=False): 

    print(f'Download all days in {downloads_day}')

    # Sig-in site
    from_bank_sicredi.entrar_sicredi()

    # Download from bank every day
    for day_download in downloads_day:

        print(f'\nDownloading bank from date: {day_download}')

        day = datetime.strptime(day_download, '%d/%m/%Y')
        name = day.strftime('%Y-%m-%d')

        # Check if file was already imported
        file_import = get_file(name)
        if file_import is not None:
            print(f'File already imported!')
            continue

        # Import to BD
        if import_bd is True:
            from_bank_sicredi.baixar_extrato(day)
        else:
            from_bank_sicredi.baixar_extrato(day)

    from_bank_sicredi.close_all()




def get_file(file_name):

    global API_KEY

    if API_KEY is None:
        return None

    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)

    with build('drive', 'v3', credentials=creds) as gdrive:
        
        try:

            file_id = get_file_id(gdrive, file_name)

            if file_id is None:
                return None

            file_path = get_file_path(gdrive, file_id)

            if file_path.find('Extratos Bancarios/Sicredi/Conta') == -1:
                return None

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        return True



def get_file_id(bd, file_name):

    response = bd.files().list(fields='nextPageToken, ' 'files(id, name)').execute()

    file_name_ok = f'{file_name}-ok.xls'
    file_name_import = f'{file_name}-import.xls'

    print(f'Searching file...: {file_name_ok} or {file_name_import}')

    for file in response.get('files', []):

        #print(f'Found file: {file.get("name")}')
        
        if file.get('name') == file_name_ok or file.get('name') == file_name_import:
            return file.get('id')
        
        time.sleep(0.1)
    
    return None


def get_file_path(gdrive, file_id):

    path_result = ''
    response = gdrive.files().get(fileId=file_id, fields='id, name, parents').execute()

    parent = response.get('parents')
    if parent:
        while True:
            folder = gdrive.files().get(fileId=parent[0], fields='id, name, parents').execute()
            parent = folder.get('parents')
            if parent is None:
                break
            path_result = folder.get('name') + '/' + path_result
            time.sleep(1)

    
    print(f'Path: {path_result}')
    return path_result