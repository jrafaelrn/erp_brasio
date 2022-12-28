from __future__ import print_function
from dataclasses import field, fields
import gspread, json, os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(f'{__file__}'))))

import cloudFunctions


def open_bd_bank():

    service_account = get_api_key()
    sa = gspread.service_account_from_dict(service_account)
    bd = sa.open("bd_bot")
    bd_sheet = bd.worksheet('bank')
    return bd_sheet



def update_pendency(id, category_erp=None, entity_erp=None, description_erp=None, status_erp=None):

    FUNCTION_NAME = 'function-bd-transaction'

    # DATA
    data = {
        'id': id,
        'category_erp': category_erp,
        'entity_erp': entity_erp,
        'description_erp': description_erp,
        'status_erp' : status_erp
    }

    # ARGS
    args = 'type=update'

    # CLOUD FUNCTION
    cloudFunctions.cloud_function(FUNCTION_NAME, data, args)


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