import requests, json, gspread, os
import pandas as pd


def open_bd_bank():

    service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    sa = gspread.service_account_from_dict(service_account)
    bd = sa.open("bd_bot")
    bd_sheet = bd.worksheet('bank')
    bd_pd = pd.DataFrame(bd_sheet.get_all_records())
    return bd_pd


def get_classifications(description):

        bd_bank = open_bd_bank()
        classes = []

        for row in bd_bank.iterrows():

            original_description = row[1]['DESCRICAO_ORIGINAL']
            original_description = original_description.strip().replace('\n', ' ').replace('\r', ' ')

            if original_description == description:

                category_erp = row[1]['CATEGORY_ERP']
                entity_erp = row[1]['ENTITY_ERP']
                id = f'{category_erp}|{entity_erp}'

                if category_erp == '' or entity_erp == '':
                    continue

                option = {'category': category_erp, 'entity': entity_erp, 'id': id}
                classes.append(option)
        
        
        if len(classes) == 0:
            return '{}'

        df = pd.DataFrame(classes)

        #Remove duplicates
        df = df.drop_duplicates(subset=['id'], keep='first')
        df_json = df.to_json(orient='records', force_ascii=False)
        
        print(df_json)

        return df_json


#################################
#   Call from Cloud Functions   #
#################################

def check(request):

    request_json = request.get_json(silent=True)
    print(f'Request JSON: {request_json}')
    
    description = request_json['description']
    response = get_classifications(description)
    print(f'Response: {response}')

    return response