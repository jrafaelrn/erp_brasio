import requests, json, gspread, os
import pandas as pd


def open_bd_bank(self):

    service_account = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    service_account_json = json.dumps(service_account)

    sa = gspread.service_account(filename=service_account_json)
    self.bd = sa.open("bd_bot")
    bd_sheet = self.bd.worksheet('bank')
    bd_pd = pd.DataFrame(bd_sheet.get_all_records())
    return bd_pd




# Call from Cloud Functions

def check(request):

    request_json = request.get_json(silent=True)
    print(f'Request JSON: {request_json}')
    
    response = None

    description = request_json['description']
    


