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

        print(f'Sending message: {content} - to chat: {chat_id}')
        link_resp = f'{self.url_base}sendMessage?chat_id={chat_id}&text={content}'
        resp = requests.get(link_resp)
        print(f'\tResponse ==>> {resp.content}')
        return resp


    
    def send_inline_options(self, options_list, chat_id):

        headers = {'Content-Type': 'application/json'}
        data = {}
        
        keyboards = []
        keyboard = []

        for option in options_list:
            
            category = option['category']
            entity = option['entity']
            keyboard_button = f'{category} - {entity}'
            
            keyboard_button_json = []
            keyboard_button_json.append({
                "text": keyboard_button, 
                "callback_data" : keyboard_button
            })
            keyboard.append(keyboard_button_json)

        
        # Add last option
        keyboard_button_json2 = []
        keyboard_button_json2.append({"text": "Nova classificação", "callback_data" : "new"})
        keyboard.append(keyboard_button_json2)

        keyboards.append(keyboard)
        data["inline_keyboard"] = keyboard

        print(f'Sending inline options: \n{data} - \nto chat: {chat_id}')
        data = json.dumps(data)

        link_resp = f'{self.url_base}sendMessage?chat_id={chat_id}&text=Escolha uma opção:&reply_markup={data}'
        response = requests.get(link_resp, headers=headers, json=data)
        print(f'\t ==>> {response.text} - {response.status_code}')



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

    print(f'Response Final ==>> {response}')
    return response



if __name__ == '__main__':

    tel = telegram()

    option_list = {'message_type': 'inline', 'content': [{'category': 'Material para escritório', 'entity': 'Kalunga', 'id': 'Material para escritório|Kalunga'}, {'category': 'Outros', 'entity': 'Genéricos', 'id': 'Outros|Genéricos'}, {'category': 'Salários', 'entity': 'Emerson Sampaio Garcia', 'id': 'Salários|Emerson Sampaio Garcia'}, {'category': 'Combustível', 'entity': 'Posto de Gasolina', 'id': 'Combustível|Posto de Gasolina'}, {'category': 'Itens para Cozinha', 'entity': 'Cartão de Crédito - Bruna Nubank', 'id': 'Itens para Cozinha|Cartão de Crédito - Bruna Nubank'}, {'category': 'Aquisição de Insumos', 'entity': 'Supermercado Diversos', 'id': 'Aquisição de Insumos|Supermercado Diversos'}, {'category': 'Marketing e Publicidade', 'entity': 'Genéricos', 'id': 'Marketing e Publicidade|Genéricos'}, {'category': 'Salários', 'entity': 'Bruna Perandini Garcia', 'id': 'Salários|Bruna Perandini Garcia'}, {'category': 'Salários', 'entity': 'Mônica Mariana Perandini Garcia', 'id': 'Salários|Mônica Mariana Perandini Garcia'}, {'category': 'Aquisição de Insumos', 'entity': 'Atacadão Jundiaí', 'id': 'Aquisição de Insumos|Atacadão Jundiaí'}, {'category': 'Marketing e Publicidade', 'entity': 'Mara Cake Fair', 'id': 'Marketing e Publicidade|Mara Cake Fair'}, {'category': 'Telefone Celular Empresarial', 'entity': 'Tim', 'id': 'Telefone Celular Empresarial|Tim'}], 'chat_id': 572312369}
    request_json = json.dumps(option_list)
    
    check(request_json)