import json, gspread, io, os, bank_sicredi
from httplib2 import Credentials
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/drive']

#################################
#       GOOGLE DRIVE API        #
#################################

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


def get_file(file_name):

    if API_KEY is None:
        return None, None
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)

    with build('drive', 'v3', credentials=creds) as gdrive:
        
        try:

            real_name, file_id = get_file_id(gdrive, file_name)
            file_path = get_file_path(gdrive, file_id)

            if file_path.find('Extratos Bancarios/') == -1:
                return None, None

            request = gdrive.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(F'Download {int(status.progress() * 100)}.')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None, None

        return real_name, file.getvalue()


def get_file_id(bd, file_name):

    response = bd.files().list(fields='nextPageToken, ' 'files(id, name)').execute()

    for file in response.get('files', []):

        print(f'Found file: {file.get("name")}')
        
        if file.get('name').find(file_name) != -1:
            return file.get('name'), file.get('id')
    
    return None


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





#################################
#      PRINCIPAL - METHOD       #
#################################

def update_bd():

    while True:
        
        file_to_import = '-import.'
        file_name, file_excel = get_file(file_to_import)

        if file_excel is None:
            print('Finished or No file found!')
            break
        
        
        df = pd.read_excel(io.BytesIO(file_excel))
        bank_sicredi.import_extrato_sicredi(df)


        # Rename file












#################################
#   Call from Cloud Functions   #
#################################

def check(request):

    request_json = request.get_json(silent=True)
    parameters = request.args
    print(f'Request JSON: {request_json}')
    print(f'Parameters: {parameters}')
    
    try:
        update_bd()
        response = {"return": "ok"}
    except:
        response = {"return": "error"}

    print(f'Response: {response}')
    return response


update_bd()