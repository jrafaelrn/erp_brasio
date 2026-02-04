import functions_framework
import logging
import sys

from httplib2 import Credentials
from datetime import datetime
from cloudevents.http import CloudEvent
from google_drive import *


logging.basicConfig(
    stream=sys.stdout, 
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    force=True
)


#################################
#      PRINCIPAL - METHOD       #
#################################

def update_bd():

    google_drive = GoogleDrive()
    banks_to_import = google_drive.get_banks_to_import()
    card_details = None
    imported = None

    for bank in banks_to_import:

        logging.info(f'.........Importing file...: {bank.file_name}')
        imported, card_details = bank.import_bank(google_drive)
        
        if imported:
            if card_details:
                if bank.card_month_year == card_details['month_year']:
                    
                    logging.info(f'File account imported! Now importing card file for month/year: {card_details["month_year"]}...')    
            else:
                logging.info(f'File account imported successfully: {bank.file_name}')
                return
        else:
            logging.warning(f'File not imported: {bank.file_name}... Trying next file...')
            
    raise Exception('No file imported!')



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
        update_bd()
        response = {"return": "ok"}
    except:
        response = {"return": "error"}

    logging.info(f'Response: {response}')
    return response


if __name__ == '__main__':
    #logging.info('Starting BD Update Banks...')
    update_bd()
    logging.info('Update BD!')