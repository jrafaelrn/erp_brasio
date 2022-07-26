from httplib2 import Credentials
import os, json, io, datetime
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/drive']
file_erp = None
df_erp = None


#################################
#       GOOGLE DRIVE API        #
#################################

def get_erp_pendency(entity):

    global file_erp
    global df_erp
    erp_pendencies = {}
    
    if file_erp is None or df_erp is None:
    
        file_erp = get_file()
    
        if file_erp is None:
            return None
    
        df_erp = pd.read_excel(io.BytesIO(file_erp))

    
    counter = 1
    options = []

    for line in df_erp.iterrows():
        
        column = line[1]['Descrição / Fornecedor']

        if (type(column) != str) or column.find('Saída do caixa') != -1:
            continue
        
        entity_line =column.split(' | ')[1]
        status_line = line[1]['Status']

        if entity_line == entity and status_line != 'Pago':

            option = {}
            due_date = (line[1]['Vencimento']).strftime('%d/%m/%Y')
            category = line[1]['Categoria']
            description = column.split(' | ')[0]
            value = line[1]['Valor Previsto']

            option['category'] = category
            option['entity'] = entity
            option['description'] = description
            option['due_date'] = due_date
            option['value'] = value

            options.append(option)
            counter += 1

    if len(options) == 0:
        return None
    
    erp_pendencies['pendencies'] = options
    return erp_pendencies




def get_file():

    API_KEY = get_api_key()

    if API_KEY is None:
        return None

    
    print(f'API KEY Found!')
    file_name = 'Consumer - Contas a Pagar TOTAL.xlsx'
    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)

    with build('drive', 'v3', credentials=creds) as gdrive:
        
        try:

            file_id = get_file_id(gdrive, file_name)
            file_path = get_file_path(gdrive, file_id)

            if file_path.find('Consumer/RELATORIOS') == -1:
                return None

            request = gdrive.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(F'Download {int(status.progress() * 100)}.')

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        return file.getvalue()



def get_file_id(bd, file_name):

    response = bd.files().list(fields='nextPageToken, ' 'files(id, name)').execute()

    for file in response.get('files', []):

        #print(f'Found file: {file.get("name")}')
        
        if file.get('name') == file_name:
            return file.get('id')
    
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


    

#################################
#   Call from Cloud Functions   #
#################################

def check(request):

    request_json = request.get_json(silent=True)
    print(f'--->> Request JSON: {request_json}')
    
    entities = request_json['entities']
    pendencies = []
    
    for entity in entities:
        response = get_erp_pendency(entity)

        if response is not None:
            pendencies.append(response)
            

    if len(pendencies) > 0:
        response_json = {'pendencies': pendencies}
    else:
        response_json = json.dumps({'error': 'No pendency found'})

    print(f'<<--- Response JSON: {response_json}')
    return response_json   
