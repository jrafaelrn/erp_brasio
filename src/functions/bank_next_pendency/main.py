import requests, json, gspread, os
import pandas as pd


def open_bd_bank():

    service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    service_account_dict = json.loads(service_account)
    sa = gspread.service_account_from_dict(service_account_dict)
    bd = sa.open("bd_bot")
    bd_sheet = bd.worksheet('bank')
    bd_pd = pd.DataFrame(bd_sheet.get_all_records())
    return bd_pd



# 1 - Searching for empty classifications and return line
def get_next_pendency():

    print('\nSearching for empty classifications...')
    bd_bank = open_bd_bank()

    # Loop over all lines
    for line in bd_bank.iterrows():

        is_import = line[1]['STATUS_ERP']
        is_classificado = line[1]['BOT_CLASSIFICATION']
        value = line[1]["VALOR"]
        valor = float(value)

        # Ao encontrar um lancamento em branco
        if is_import == '' and not(is_classificado == 1) and valor < 0:
            line_dict = line[1]  
            print(f'Found empty classifications - ID: {line_dict["ID"]}')
            return line_dict

    return None


#################################
#   Call from Cloud Functions   #
#################################

def check(request):

    request_json = request.get_json(silent=True)
    print(f'Request JSON: {request_json}')
    
    response = get_next_pendency()

    if response is not None:
        response_json = response.to_json()
    else:
        response_json = json.dumps({'error': 'No pendency found'})
    
    # Replace slashes
    response_json = response_json.replace('\\', '')
    print(f'Response: {response_json}')

    return response_json