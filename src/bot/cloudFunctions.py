import os, json, requests

def cloud_function(FUNCTION_NAME, DATA):

    REGION = os.environ.get("REGION")
    GCP_PROJECT_ID =  os.environ.get("GCP_PROJECT_ID")

    data = json.dumps(DATA)
    headers = {'Content-Type': 'application/json'}
    link = f'https://{REGION}-{GCP_PROJECT_ID}.cloudfunctions.net/{FUNCTION_NAME}'

    resp = requests.post(link, data = data, headers = headers)

    if resp.status_code == 200:
        print(f'Function {FUNCTION_NAME} executed!')
    else:
        print(f'Function {FUNCTION_NAME} not executed! - Data: {data}')