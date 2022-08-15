import os, json, requests

##############################################
#               CLOUD FUNCTION               #
##############################################

def send_message(message, chat_id):

    FUNCTION_NAME = 'function-telegram'

    # DATA
    data = {
        'message_type': 'text',
        'content' : message,
        'chat_id': chat_id
    }

    # CLOUD FUNCTION
    cloud_function(FUNCTION_NAME, data)



def cloud_function(FUNCTION_NAME, DATA, ARGS=None):

    REGION = os.environ.get("REGION")
    GCP_PROJECT_ID =  os.environ.get("GCP_PROJECT_ID")

    data = json.dumps(DATA)
    headers = {'Content-Type': 'application/json'}
    link = f'https://{REGION}-{GCP_PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}'

    if ARGS:
        link += f'?{ARGS}'
    
    resp = requests.post(link, data = data, headers = headers)

    if resp.status_code == 200:
        #print(f'Function {FUNCTION_NAME} executed!')
        #print(f'Response: {resp.status_code} - Text: {resp.text} - Content: {resp.content}')
        
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

