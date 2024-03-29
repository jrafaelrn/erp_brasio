from __future__ import print_function
from dataclasses import field, fields
from gc import callbacks
from flask import escape

import os, sys, json, requests, base64


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



    def sendMessage(self, content, chat_id):

        print(f'<<--- Sending message: {content} - to chat: {chat_id}')
        link_resp = f'{self.url_base}sendMessage?chat_id={chat_id}&text={content}'
        
        resp = requests.get(link_resp)
        print(f'\t<<--- Send message - Response: {resp.status_code} - {resp.text}')
        
        if resp.status_code == 200:
            return "OK - Message sent"
        else:
            return "Error - Message not sent"


    
    def send_inline_options(self, options_list, chat_id):

        headers = {'Content-Type': 'application/json'}
        data = {}        
        keyboards = []
        keyboard = []
        counter = 0

        for option in options_list:
            
            keyboard_button_json = []
            keyboard_button_json.append({
                "text": option, 
                "callback_data" : counter
            })
            keyboard.append(keyboard_button_json)
            counter += 1


        keyboards.append(keyboard)
        data["inline_keyboard"] = keyboard

        print(f'<<--- Sending inline options: \n{data} - \nto chat: {chat_id}')
        data = json.dumps(data)

        link_resp = f'{self.url_base}sendMessage?chat_id={chat_id}&text=Escolha uma opção:&reply_markup={data}'
        response = requests.get(link_resp, headers=headers, json=data)
        print(f'\<<--- Response: {response.status_code}')

        if response.status_code == 200:
            return "OK - Message inline sent"
        else:
            return "Error - Message inline not sent"



# Call from Cloud Functions

def check(request):

    request_json = request.get_json(silent=True)
    print(f'Request jSON: {request_json}')
    
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
    
    elif msg_type == 'inline':
            
            try:
                response = telegram_bot.send_inline_options(msg_content, msg_chat_id)
            except Exception as e:
                print(e)
                response = 'Ocorreu um erro ao enviar a mensagem inline.'

    else:
        response = 'Invalid payload'

    print(f'<<--- Response Final--->> {response}')
    return response