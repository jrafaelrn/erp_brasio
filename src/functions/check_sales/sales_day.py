from __future__ import print_function

import io, os, sys

from httplib2 import Credentials
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import base64
import keys

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials





def check(event, context):

    if type(event) != str:
        payload = base64.b64decode(event['data']).decode('utf-8')
    else:
        payload = event

    if payload == 'check_sales_day':
        return check_day()
    else:
        return 'Invalid payload'

        

def check_day():
    
    today = datetime.datetime.now().strftime('%d/%m/%Y')
    GOAL = 600

    total_sales_day = get_bank_resume_day(today)

    #Format to currency
    total_sales_day_currency = (f'R$ {total_sales_day:.2f}').replace('.', ',')
    percentual_sales_goal = (f'{(total_sales_day / GOAL) * 100:.0f} %').replace('.', ',')

    if total_sales_day > GOAL:
        msg = f'UHUUUUL... META ATINGIDA!!\nTotal dia: {os.linesep}{total_sales_day_currency} {os.linesep}({percentual_sales_goal})'
        return msg

    
    msg = f'Quase lá...Total vendas do dia:  {os.linesep}{total_sales_day_currency}  {os.linesep}({percentual_sales_goal})'
    return msg




def get_bank_resume_day(day):

    file_bank_today = f'{day}.xls'
    file_id = '1KuPmvGq8yoYgbfW74OENMCB5H0n_2Jm9'
    creds = Credentials.from_authorized_user_file(keys.GOOGLE_DRIVE_KEY)
    
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    with build('drive', 'v3', credentials=keys.GOOGLE_DRIVE_KEY) as bd:
        
        try:
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




if __name__ == '__main__':
    check('check_sales_day', '')