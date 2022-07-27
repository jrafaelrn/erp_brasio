import requests, json, os

#################################
#       GOOGLE FUNCTION         #
#################################

def insert(DATA, ARGS=None):

    REGION = os.environ.get("REGION")
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
            except:
                response = resp.content
        except:
            response = resp.text    

        return response
    
    else:
        print(f'!!! Function {FUNCTION_NAME} not executed! - Data: {data} - Status Code: {resp.status_code} - Text: {resp.text}')
        return None


