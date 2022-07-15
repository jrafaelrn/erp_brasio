import datetime
import base64
import os
import secrets
from googleapiclient.discovery import build


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

    
    with build('drive', 'v3', delevoperKey=${{ secrets.GOOGLE_SERVICE_ACCOUNT_KEY }}) as bd:



if __name__ == '__main__':
    check('check_sales_day', '')