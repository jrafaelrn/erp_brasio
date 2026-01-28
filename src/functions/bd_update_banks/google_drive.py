import io
import json
import os
import logging

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = ['https://www.googleapis.com/auth/drive']
files_to_import = []
account_name = None
API_KEY = None


#################################
#       GOOGLE DRIVE API        #
#################################

def get_api_key():

    api_key = None
    logging.info('Getting API KEY...')
    
    try:
        
        try:
            file_service_account = 'key.json'
            actual_folder = os.path.dirname(os.path.abspath(__file__))
            actual_folder = os.path.join(actual_folder, file_service_account)
    
            #Open file
            file = open(actual_folder, 'r')
            file_content_string = file.read()
    
            api_key = json.loads(file_content_string)
            logging.info('API KEY Found from File!')
            
        except Exception as e:
            logging.error(f'Error: {e}')            
            service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
            api_key = json.loads(service_account)
            logging.info('API KEY Found from Environment!')

    except Exception as e:
        logging.error(f'Error: {e}')
        api_key = None    
    
    return api_key





def get_files_to_import():

    global files_to_import
    global API_KEY
    
    API_KEY = get_api_key()
    logging.info('Searching for files to import...')

    if API_KEY is None:
        logging.error('API KEY not found! Impossible to continue.')
        return False
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)
    gdrive = build('drive', 'v3', credentials=creds, cache_discovery=False)
    
    try:
        response = gdrive.files().list(fields='nextPageToken, ' 'files(id, name)').execute()
        
        for file in response.get('files', []):
            
            name_file = file.get('name')
            logging.info(f'Analyzing File: {name_file}')
            if name_file.find('-import') == -1:
                continue
            
            id_file = file.get('id')
            path_file = get_file_path(gdrive, id_file)

            file_to_import = {}
            file_to_import['name'] = name_file
            file_to_import['id'] = id_file
            file_to_import['path'] = path_file.upper()
            logging.info(f'File ADD to import: {file_to_import}')
            files_to_import.append(file_to_import)


        logging.info(f'==== Finished Search --> Files to import: {files_to_import}')
        gdrive.close()
        return True
        
    except Exception as error:
        logging.error(f'An error occurred: {error}')
        gdrive.close()
        return False




def get_file(file_id):
    
    global API_KEY
    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)
    gdrive = build('drive', 'v3', credentials=creds, cache_discovery=False)
    
    try:
        request = gdrive.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logging.info(f'Download {int(status.progress() * 100)}%')
        gdrive.close()
        return file.getvalue()

    except HttpError as error:
        logging.error(f'An error occurred: {error}')
        logging.error('Probably any file is found.')
        gdrive.close()
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

    logging.info(f'Path: {path_result}')
    return path_result



def rename_file(file_id, old_name_file, new_file_name):

    global API_KEY
    new_name_file = old_name_file.replace('-import', f'-{new_file_name}')
    logging.info(f'New name file: {new_name_file}')
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(API_KEY, SCOPES)
    gdrive = build('drive', 'v3', credentials=creds, cache_discovery=False)
    
    try:
        file_metadata = {
            'name': new_name_file
        }

        gdrive.files().update(fileId=file_id, body=file_metadata).execute()
        gdrive.close()
        return True

    except HttpError as error:
        logging.error(f'An error occurred: {error}')
        gdrive.close()
        return False



def check_if_file_exists(path_filter, name_filter):

    global files_to_import

    for file in files_to_import:
        if file['path'].find(path_filter.upper()) != -1 and file['name'] == name_filter:
            return True, file['id']

    return False, None


