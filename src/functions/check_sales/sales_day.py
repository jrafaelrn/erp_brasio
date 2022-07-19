from __future__ import print_function
from dataclasses import field, fields
from httplib2 import Credentials
from datetime import datetime

import io, os, sys, base64, json
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    from credentials.keys import GOOGLE_SERVICE_ACCOUNT_KEY
    from credentials import keys   
except ImportError:
    print('No credentials.py file found.')
    

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = ['https://www.googleapis.com/auth/drive']



def check(event, context):

    if type(event) != str:
        payload = base64.b64decode(event['data']).decode('utf-8')
    else:
        payload = event

        response = None

    if payload == 'check_sales_day':

        try:
            response = check_day()
        except Exception as e:
            print(e)
            response = 'Ocorreu um erro ao verificar o dia. Uma nova tentativa será feita em breve.'
    
    else:
        response = 'Invalid payload'

    print(f'Sales Day: {response}')
    return response

        

def check_day():
    
    GOAL = 600

    total_sales_day = get_bank_resume_day()

    #Format to currency
    total_sales_day_currency = (f'R$ {total_sales_day:.2f}').replace('.', ',')
    percentual_sales_goal = (f'{(total_sales_day / GOAL) * 100:.0f} %').replace('.', ',')

    if total_sales_day > GOAL:
        msg = f'UHUUUUL... META ATINGIDA!!\nTotal dia: {os.linesep}{total_sales_day_currency} {os.linesep}({percentual_sales_goal})'
        return msg

    
    msg = f'Quase lá...Total vendas do dia:  {os.linesep}{total_sales_day_currency}  {os.linesep}({percentual_sales_goal})'
    return msg




def get_bank_resume_day():

    today = datetime.now().strftime('%Y-%m-%d')
    today_ptbr = datetime.now().strftime('%d/%m/%Y')
    file_bank_today = f'{today}.xls'
    
    file = get_file(file_bank_today)
    df = pd.read_excel(io.BytesIO(file))

    sales_day = calculate('14/07/2022', df)

    return sales_day

    


def get_file(file_name):

    GOOGLE_SERVICE_ACCOUNT_KEY = get_api_key()

    if GOOGLE_SERVICE_ACCOUNT_KEY is None:
        print('No API key found.')
        return
    else:
        print('API key found.')


    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SERVICE_ACCOUNT_KEY, SCOPES)

    with build('drive', 'v3', credentials=creds) as bd:
        
        try:

            file_id = get_file_id(bd, file_name)
            request = bd.files().get_media(fileId=file_id)
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



def get_file_id(bd, filne_name):

    response = bd.files().list(fields='nextPageToken, ' 'files(id, name)').execute()

    for file in response.get('files', []):

        #print(f'Found file: {file.get("name")}')
        
        if file.get('name') == filne_name:
            return file.get('id')
    
    return None




def calculate(day, bd):

    total = 0
    
    # Loop through rows
    for row in bd.iterrows():

        try:

            data = datetime.strptime(row[1][0], '%d/%m/%Y')
            description = row[1][1]
            tipo = row[1][2]
            valor = float(row[1][3])

            if valor > 0 and description.find('40847221000114') == -1:
                total += valor
        
        except Exception as e:
            #print(e)
            continue

    return total



def get_api_key():
    
    try:

        secret_google_manager = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
        api_key = json.loads(secret_google_manager)['GOOGLE_SERVICE_ACCOUNT_KEY']
        return api_key

        try:
            api_key = keys.GOOGLE_SERVICE_ACCOUNT_KEY 
            return api_key
        except Exception as e:
            print(f'Error: {e}')
            return None
            
    except Exception as e:
        print(f'Error: {e}')    
        return None


