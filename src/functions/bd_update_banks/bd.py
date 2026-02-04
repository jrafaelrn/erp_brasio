import requests
import json
import os
import logging

logger = logging.getLogger()

#################################
#       GOOGLE FUNCTION         #
#################################

def insert(DATA, ARGS=None):

    print(f'<<--- Trying insert data into Google Sheets... - {DATA}')
    
    REGION = os.environ.get('REGION')
    GCP_PROJECT_ID =  os.environ.get("GCP_PROJECT_ID")    
    FUNCTION_NAME = 'function-bd-transaction'
    ARGS = 'type=insert'

    data = json.dumps(DATA)
    headers = {'Content-Type': 'application/json'}
    link = f'https://{REGION}-{GCP_PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}?{ARGS}'
    print(f'Link: {link}')
    
    resp = requests.post(link, data = data, headers = headers)

    if resp.status_code == 200:
        print(f'Function {FUNCTION_NAME} executed! - Response Text: {resp.text}')
        
        try:
            try:
                response = json.loads(resp.content)
            except Exception as e:
                response = resp.content
                logger.warning(f'Error when parse JSON response: {e}')
        except Exception as e:
            response = resp.text    
            logger.error(f'Error when getting response text: {e}')

        return response
    
    else:
        raise Exception(f'Function {FUNCTION_NAME} not executed! - Status Code: {resp.status_code} - Text: {resp.text}')
    


