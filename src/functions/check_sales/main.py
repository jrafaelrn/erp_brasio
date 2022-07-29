from __future__ import print_function
from dataclasses import field, fields
from httplib2 import Credentials
from datetime import datetime, timedelta

import io, os, sys, base64, json, sender, random, gspread
import pandas as pd


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
    print(f'Payload: {payload}')

    try:
        response = check_sales_day()
    except Exception as e:
        print(e)
        response = 'Ocorreu um erro ao verificar o dia. Uma nova tentativa será feita em breve.'
    
    else:
        response = 'Invalid payload'

    print(f'Sales Day: {response}')
    return response

        

def check_sales_day():
    
    GOAL = 600
    msgs_bellow = [
        'O dia não tá fácil, mas ainda não acabou. Vamos lá!',
        'Quase lá, bota esse corpo pra jogooo e booora vender mais!',
        'Ainda dá tempo de vender mais, correeeeee!!!',
    ]

    msgs_above = [
        'Vivaaaa, suas vendas tão demais!! Parabéns!',
        'Meta batida com sucessooo!! Luxooo!!',
        'Vamos que vamos, mais um dia de sucesso!',
        'Mais um dia pras vitoriosas!! Sucesso!!'
    ]

    total_sales_day, details, last_update = get_bank_resume_day()

    if total_sales_day is None:
        return 'Não foi possível verificar as vendas do dia. Próxima tentativa será feita em 2 horas.'

    #Format to currency
    total_sales_day_currency = (f'R$ {total_sales_day:.2f}').replace('.', ',')
    meta_currency = (f'R$ {GOAL:.2f}').replace('.', ',')
    percentual_sales_goal = (f'{(total_sales_day / GOAL) * 100:.0f} %').replace('.', ',')

    msg = ''

    #Random message
    if total_sales_day > GOAL:
        msg = msgs_above[random.randint(0, len(msgs_above) - 1)]
    else:
        msg = msgs_bellow[random.randint(0, len(msgs_bellow) - 1)]
    
    msg = f'{msg} {os.linesep}'
    msg += f'Meta: {meta_currency} {os.linesep}'
    msg += f'Vendas: {total_sales_day_currency} {os.linesep}'
    msg += f'{percentual_sales_goal} {os.linesep}{os.linesep}'

    for detail in details['total']:
        msg += f'{detail} {os.linesep}'
    
    msg += f'{os.linesep}Data atualização: {last_update}'
    

    chats_id = get_chats_id()

    if len(chats_id) == 0:
        return 'Vendas calculadas = {msg}, \n mas não foi possível enviar a mensagem pois não há chats cadastrados.'

    for chat_id in chats_id:
        sender.send_message(msg, chat_id)


    return 'Vendas calculadas e enviadas com sucesso.'




def get_bank_resume_day():

    today = datetime.now().strftime('%Y-%m-%d')
    today_ptbr = datetime.now().strftime('%d/%m/%Y')
    file_bank_today = f'{today}.xls'
    
    file, last_update = get_file(file_bank_today)

    if file is None:
        return None

    df = pd.read_excel(io.BytesIO(file))
    df_pd = pd.DataFrame(df)

    sales_day, details = calculate(df_pd)
    return sales_day, details, last_update



def calculate(bd):

    total = 0
    detalhes = {}
    detalhes_array = []
    MY_CNPJ = os.environ.get('MY_CNPJ')
    
    # Loop through rows
    for row in bd.iterrows():

        try:

            data = datetime.strptime(row[1][0], '%d/%m/%Y')
            description = row[1][1]
            tipo = row[1][2]
            valor = float(row[1][3])

            if valor > 0 and description.find(MY_CNPJ) == -1:
                total += valor
                valor_ptbr = (f'R$ {valor:.2f}').replace('.', ',')
                detalhe_str = f'{description} - {valor_ptbr}'
                detalhes_array.append(detalhe_str)
        
        except Exception as e:
            #print(e)
            continue
    
    detalhes['total'] = detalhes_array

    return total, detalhes



def get_chats_id():

    service_account = get_api_key()
    sa = gspread.service_account_from_dict(service_account)
    bd = sa.open("bd_bot")
    bd_sheet = bd.worksheet('chats')
    
    chats = bd_sheet.get_all_records()
    chats_id = []

    for row in chats:
        chats_id.append(row['CHAT_ID'])

    return chats_id




#################################
#       GOOGLE DRIVE API        #
#################################

def get_file(file_name):

    GOOGLE_SERVICE_ACCOUNT_KEY = get_api_key()

    if GOOGLE_SERVICE_ACCOUNT_KEY is None:
        print('No API key found.')
        return

    print('API key found.')
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SERVICE_ACCOUNT_KEY, SCOPES)

    with build('drive', 'v3', credentials=creds) as bd:
        
        try:

            file_id, last_update = get_file_id(bd, file_name)
            file_path = get_file_path(bd, file_id)

            if file_path.find('Extratos Bancarios') == -1:
                print('Today file not found.')
                return None

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

        
        return file.getvalue(), last_update



def get_file_id(bd, filne_name):

    response = bd.files().list(fields='nextPageToken, ' 'files(id, name)').execute()

    for file in response.get('files', []):

        #print(f'Found file: {file.get("name")}')
        
        if file.get('name') == filne_name:

            last_update = get_time_stamp(bd, file)
            return file.get('id'), last_update
    
    return None, None



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



def get_time_stamp(bd, file):

    try:
        
        last_update = bd.files().get(fileId=file.get('id'), fields='modifiedTime').execute()
        last_update_time = last_update['modifiedTime']
        last_update_time_datetime = datetime.strptime(last_update_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        last_update_time_brasilia = last_update_time_datetime - timedelta(hours=3)
        last_update_time_brasilia_str = last_update_time_brasilia.strftime('%d/%m/%Y %H:%M:%S')
        return last_update_time_brasilia_str
    
    except Exception as e:
        print(f'Error: {e}')
        return None