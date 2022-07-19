from __future__ import print_function
from dataclasses import field, fields
from flask import escape

import os, sys, json, requests, base64, functions_framework


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(f'{__file__}'))))

try:
    #from credentials.keys import TELEGRAM_API_KEY
    from credentials import keys   
except ImportError:
    print('No credentials.py file found.')



def get_api_key():

    api_key = None
    
    try:
        try:
            api_key = keys.TELEGRAM_API_KEY 
            
        except Exception as e:
            print(f'Error - Get KEY from file: {e}')
            api_key = None
            
        api_key = os.environ.get("TELEGRAM_API_KEY")

    except Exception as e:
        print(f'Error - Get KEY from environment: {e}')    
        api_key = None

    return api_key





class telegram(object):

    url_base = 'https://api.telegram.org/bot'

    def __init__(self):

        TELEGRAM_API_KEY = get_api_key()

        if TELEGRAM_API_KEY is None:
            print('No API key found.')
            return
        else:
            print(f'API key found!')


        self.url_base = f'{self.url_base}{TELEGRAM_API_KEY}/'



    def get_messages_by_id(self, update_id):

        link_request = f'{self.url_base}getUpdates?timeout=50'
        if update_id:
            link_request += f'&offset={update_id + 1}'
        resp = requests.get(link_request)
        return json.loads(resp.content)



    def sendMessage(self, content, chat_id):

        #print(f'Enviando mensagem Texto: {mensagem}')
        link_resp = f'{self.url_base}sendMessage?chat_id={chat_id}&text={content}'
        resp = requests.get(link_resp)
        print(f'\tResponse ==>> {resp.content}')


    
    def send_inline_options(self, options_list, chat_id):

        headers = {'Content-Type': 'application/json'}
        data = {}
        data['reply_markup'] = {}
        
        keyboards = []
        keyboard = []

        for option in options_list.iterrows():
            
            grupo = option[1]['grupo']
            fornecedor = option[1]['fornecedor']
            keyboard_button = f'{grupo} - {fornecedor}'
            
            keyboard_button_json = {}
            keyboard_button_json['text'] = keyboard_button
            keyboard.append(keyboard_button_json)
        
        # Add last option
        keyboard_button_json2 = {}
        keyboard_button_json2['text'] = 'Nova classificação'
        keyboard.append(keyboard_button_json2)

        keyboards.append(keyboard)
        data['keyboard'] = keyboards
        data['one_time_keyboard'] = True
        #data['resize_keyboard'] = True

        data = json.dumps(data)

        link_resp = f'{self.url_base}sendMessage?chat_id={chat_id}&text=Escolha uma opção:&reply_markup={data}'
        response = requests.get(link_resp, headers=headers, json=data)
        print(f'\t ==>> {response.text}')



# Call from Cloud Functions

def check(request):

    request_json = request.get_json(silent=True)
    request_args = request.args

    print(f'Request jSON: {request_json}')
    print(f'Request ARGS: {request_args}')
    
    response = None

    msg_type = request_json['message_type']
    msg_content = request_json['content']
    msg_chat_id = request_json['chat_id']

    # Create Telegram
    telegram_bot = telegram()

    if msg_type == 'text':

        try:
            response = telegram_bot.sendMessage(msg_content, msg_chat_id)
        except Exception as e:
            print(e)
            response = 'Ocorreu um erro ao enviar a mensagem.'
    
    else:
        response = 'Invalid payload'

    print(f'Response: {response}')
    return response