import io
import json
import logging
import os
import re

from dataclasses import dataclass, field
from typing import List
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from bank import Bank
from bank_sicredi import BankSicredi

logger = logging.getLogger()


#################################
#       GOOGLE DRIVE API        #
#################################

@dataclass
class GoogleDrive():
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    files_to_import: List[dict] = field(default_factory=list)
    banks_to_import: List[Bank] = field(default_factory=list)
    account_name: str = None
    API_KEY: dict = field(default=None, init=False)
    
    
    def __post_init__(self):
        self.API_KEY = self.get_api_key()
    

    def get_api_key(self):

        logger.info('Getting API KEY...')
        api_key = None
        
        try:
            
            try:
                file_service_account = 'key.json'
                actual_folder = os.path.dirname(os.path.abspath(__file__))
                actual_folder = os.path.join(actual_folder, file_service_account)
        
                #Open file
                with open(actual_folder, 'r') as file:
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
            raise Exception('API KEY not found!')
        
        return api_key





    def get_banks_to_import(self):
        
        logger.info('Searching for files to import...')
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.API_KEY, self.SCOPES)
        gdrive = build('drive', 'v3', credentials=creds, cache_discovery=False)
        
        try:
            response = gdrive.files().list(fields='nextPageToken, ' 'files(id, name)').execute()
            
            for file in response.get('files', []):
                
                name_file = file.get('name')
                #logger.info(f'Analyzing File: {name_file}')
                if name_file.find('-import') == -1:
                    continue
                
                id_file = file.get('id')
                path_file = self.get_file_path(gdrive, id_file).upper()

                new_bank = self.get_bank(name_file, id_file, path_file)
                logger.info(f'Bank ADD to import: {new_bank}')
                self.banks_to_import.append(new_bank)


            logger.info(f'==== Finished Search --> Banks to import: {self.banks_to_import}')
            gdrive.close()
            return self.banks_to_import
            
        except Exception as error:
            logger.error(f'An error occurred: {error}')
            gdrive.close()
            return []



    def get_bank(self, name_file, id_file, path_file):
        
        bank = None
        get_bank_name = self.get_bank_name_from_path(path_file)
        
        
        if get_bank_name.find('SICREDI') != -1:
        
            bank = BankSicredi(
                bank_name=get_bank_name,
                file_name=name_file,
                file_id=id_file,
                file_path=path_file
            )
            
        return bank
        
            

    def get_bank_name_from_path(self, path_file):
        
        bank_name = None
        
        if path_file.find('SICREDI') != -1:
            
            # Obtem o nome do banco, extraindo parte da string 'path_file', 
            # que está junto ao nome SICREDI
            bank_name = re.search(r'(SICREDI[-_]?[A-Z0-9\-]*)', path_file)
            
        return bank_name.group(1) if bank_name else None



    def get_file(self, file_id):
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.API_KEY, self.SCOPES)
        gdrive = build('drive', 'v3', credentials=creds, cache_discovery=False)
        
        try:
            request = gdrive.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f'Download {int(status.progress() * 100)}%')
            gdrive.close()
            return file.getvalue()

        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            logger.error('Probably any file is found.')
            gdrive.close()
            return None



    def get_file_path(self, gdrive, file_id):

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

        #logger.info(f'Path: {path_result}')
        return path_result



    def rename_file(self, file_id, old_name_file, new_file_name):

        new_name_file = old_name_file.replace('-import', f'-{new_file_name}')
        logger.info(f'New name file: {new_name_file}')
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.API_KEY, self.SCOPES)
        gdrive = build('drive', 'v3', credentials=creds, cache_discovery=False)
        
        try:
            file_metadata = {
                'name': new_name_file
            }

            gdrive.files().update(fileId=file_id, body=file_metadata).execute()
            gdrive.close()
            return True

        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            gdrive.close()
            return False



    def check_if_file_exists(self, path_filter, name_filter):

        for file in self.files_to_import:
            if file['path'].find(path_filter.upper()) != -1 and file['name'] == name_filter:
                return True, file['id']

        return False, None


