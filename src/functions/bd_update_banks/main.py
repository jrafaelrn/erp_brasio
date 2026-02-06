from datetime import datetime

import functions_framework
import google_drive
import json
import logging
import os
import sys
import requests

from cloudevents.http import CloudEvent


logging.basicConfig(
    stream=sys.stdout, 
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    force=True
)

banks = None
google_drive_instance = None


def get_banks_to_import():
    global banks
    global google_drive_instance
    if banks is None:
        google_drive_instance = google_drive.GoogleDrive()
        banks = google_drive_instance.get_banks_to_import()



#################################
#      PRINCIPAL - METHOD       #
#################################

def update_bd():

    global banks
    global google_drive_instance
    card_details = None
    imported = None
    account_files = [bank for bank in banks if not bank.is_card_file]   

    for bank in account_files:

        logging.info(f'.........Importing file...: {bank.file_name}')
        debug_to_me(f'➡️ Importing file...: {bank.file_name}')
        imported, card_details = bank.import_bank(google_drive_instance)
        
        if imported:
            logging.info(f'File {bank.file_name} from account {bank.bank_name} imported!')    
            logging.info(f'Total of transactions imported: {bank.counter}')
            logging.info(f'Has card to import: {card_details}')
            debug_to_me(f'✅ File {bank.file_name} from account {bank.bank_name} imported!')
            debug_to_me(f'Total transactions: {bank.counter}.')
            debug_to_me(f'Has card to import: {card_details}')

            if card_details:
                logging.info(f'Importing card from bank file: {bank.file_name}...')
                debug_to_me(f'💳 Importing card from bank file: {bank.file_name}...')
                card_bank = get_card_bank(card_details['date_payment'])
                if card_bank is None:
                    logging.error(f'Card bank not found for payment date: {card_details["date_payment"]}!')
                    raise Exception('Card bank not found!')
                card_bank.import_bank(google_drive_instance, card_details)
                logging.info(f'File {card_bank.file_name} from card {card_bank.bank_name} imported!')
                logging.info(f'Total of transactions imported: {card_bank.counter}')
                debug_to_me(f'🎉 File {card_bank.file_name} from card {card_bank.bank_name} imported!')
                debug_to_me(f'Total transactions: {card_bank.counter}')
                return
                    
            else:
                logging.info(f'File account imported successfully: {bank.file_name}')
                debug_to_me(f'🎉 File account imported successfully: {bank.file_name}')
                return
        else:
            logging.warning(f'File not imported: {bank.file_name}... Trying next file...')
            debug_to_me(f'File not imported: {bank.file_name}... Trying next file...')
        

    debug_to_me('No file imported!')
    raise Exception('No file imported!')



def get_card_bank(payment_date):

    global banks
    
    # Convert string to date (pt-BR format  dd/MM/yyyy)
    if type(payment_date) is str:
        payment_date = datetime.strptime(payment_date, '%d/%m/%Y')

    # Filter banks where `is_card_file` is True
    card_banks = [bank for bank in banks if bank.is_card_file]

    for bank in card_banks:
        card_file_date = datetime.strptime(bank.card_file_name, '%Y-%m-%d')
        if card_file_date.date() == payment_date.date():
            return bank

    return None


def debug_to_me(mensagem):

    URL_WEBHOOK_DEBUG = os.environ.get('URL_WEBHOOK_DEBUG')
    DATA = json.dumps({"mensagem": mensagem})
    HEADERS = {'Content-Type': 'application/json'}  

    if URL_WEBHOOK_DEBUG:
        try:
            requests.post(URL_WEBHOOK_DEBUG, data=DATA, headers=HEADERS)
        except Exception as e:
            logging.error(f'Error sending debug message: {e}')


#################################
#   Call from Cloud Functions   #
#################################

@functions_framework.cloud_event
def check(cloud_event: CloudEvent):

    logging.info('Starting BD Update Banks...')
    
    payload = cloud_event.data
    response = None
    logging.info(f'Payload: {payload}')
    
    try:
        get_banks_to_import()
        update_bd()
        response = {"return": "ok"}
    except Exception as e:
        logging.error(f'XXX XXX Error updating BD: {e}')    
        response = {"return": "error"}

    logging.info(f'Response: {response}')
    return response


if __name__ == '__main__':
    #logging.info('Starting BD Update Banks...')
    get_banks_to_import()
    update_bd()
    logging.info('Update BD!')