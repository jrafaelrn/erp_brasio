import base64, json


def check(event, context):

    if type(event) != str:
        payload = base64.b64decode(event['data']).decode('utf-8')
    else:
        payload = event

    response = None
    print(f'Payload: {payload}')

    try:
        response = import_all_banks()
    except Exception as e:
        print(e)
        response = 'Ocorreu um erro ao verificar o dia. Uma nova tentativa será feita em breve.'
    
    else:
        response = 'Invalid payload'

    print(f'Sales Day: {response}')
    return response

        

def import_all_banks():
    import_sicredi()
    import_pagbank()


def import_sicredi():
    pass

def import_pagbank():
    pass