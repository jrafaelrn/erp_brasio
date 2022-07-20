import time, requests, json, os

first_time = True

def start_bot():

    print('Starting bot...')
    update_id = None

    while True:
           
            atualizacao = get_messages_by_id(update_id)
            dados = atualizacao['result']

            if dados:

                for dado in dados:

                    try:
                        update_id = dado['update_id']
                        chat_id = dado['message']['from']['id']
                        mensagem = str(dado['message']['text'])
                        nome = dado['message']['chat']['first_name']
                        username = dado['message']['chat']['username']
                        msg = f'Mensagem Recebida: [{mensagem}] - Chat ID: {chat_id} - Nome: {nome} - Update ID: {update_id} - Username: {username}'
                        print(msg)                     


                        if validate(username):
                            reply(mensagem, chat_id)
                        else:
                            msg.enviarMensagem('Usuário não autorizado!', chat_id)

                    except Exception as e:
                        print(f'\nErro: {e}')
                        continue

            time.sleep(3)



def get_messages_by_id(update_id):

    API_KEY = get_key_from_os('TELEGRAM_API_KEY')
    url_base = f'https://api.telegram.org/bot{API_KEY}/'
    global first_time

    if first_time:
        link_request = f'{url_base}getUpdates'
        first_time = False
    
    else:
        link_request = f'{url_base}getUpdates?timeout=5'

        if update_id:
            link_request += f'&offset={update_id + 1}'
    
    #print(f'\nLink request: {link_request}')    
    resp = requests.get(link_request)
    
    print(f'Response: {resp.status_code} - {resp.text}')
    return json.loads(resp.content)


##############################################
#                  SECURITY                  #
##############################################

def get_key_from_os(KEY):

    api_key = None
    
    try:            
        api_key = os.environ.get(KEY)

    except Exception as e:
        print(f'Error - Get KEY from environment: {e}')    
        api_key = None

    return api_key


def validate(self, user):

    users = get_key_from_os('USERS')

    if user in users:
        return True
    else:
        print(f'\nUsuário {user} não autorizado!')
        return False



##############################################
#                REPLY MESSAGE               #
##############################################

def reply(message, chat_id):

    message = message.lower()
    reply_message = get_reply(message)

    send_message(reply_message, chat_id)



def get_reply(message):

    if message == '/start' or message == 'menu':
        return 'Bem vindo ao bot!'
    elif message == '/help':
        return 'Comandos disponíveis: /start'
    elif message == '/stop':
        return 'Bot desligado!'
    else:
        return 'Comand not found! Try: MENU'



def send_message(message, chat_id):

    REGION = os.environ.get("REGION")
    FUNCTION_NAME = 'function-telegram'

    # DATA
    data = {
        'message_type': 'text',
        'content' : message,
        'chat_id': chat_id
    }

    link = f'https://{REGION}.cloudfunctions.net/{FUNCTION_NAME}\" -H \"Content-Type:application/json\" --data \'{data}'
    resp = requests.post(link)

    if resp.status_code == 200:
        print(f'\nMessage successfully sent to chat ID: {chat_id}')
    else:
        print(f'\nError while sending message to chat ID: {chat_id} - {resp.status_code} - {resp.text}')


if __name__ == '__main__':
    msg = get_messages_by_id( None)
    msg = get_messages_by_id( None)