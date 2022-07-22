import time, requests, json, os, chat

chats = []

def start_bot():

    print('Starting bot...')
    update_id = None

    while True:
           
        try:

            atualizacao = get_messages_by_id(update_id)
            dados = atualizacao['result']

            if dados:
                for dado in dados:

                    update_id = dado['update_id']
                    chat_id = dado['message']['from']['id']
                    mensagem = str(dado['message']['text'])
                    nome = dado['message']['chat']['first_name']
                    username = dado['message']['chat']['username']
                    msg = f'Mensagem Recebida: [{mensagem}] - Chat ID: {chat_id} - Nome: {nome} - Update ID: {update_id} - Username: {username}'
                    print(msg)                     

                    if validate(username):
                        interact(username, chat_id, mensagem)
                    else:
                        chat.send_message('text', 'Usuário não autorizado!', chat_id)

        except Exception as e:
            print(f'Erro: {e}')
            continue

        time.sleep(2)



def get_messages_by_id(update_id):

    API_KEY = get_key_from_os('TELEGRAM_API_KEY')
    url_base = f'https://api.telegram.org/bot{API_KEY}/'

    link_request = f'{url_base}getUpdates'

    if update_id:
        link_request += f'?offset={update_id + 1}'
    
    #print(f'Link request: {link_request}')  
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


def validate(user):

    user = user.lower()
    users = get_key_from_os('USERS')

    if user in users:
        return True
    else:
        print(f'Usuário {user} não autorizado!')
        return False



##############################################
#                  INTERACT
##############################################

def interact(username, chat_id, message):

    if len(chats) == 0:
        new_chat = chat.chat(username, chat_id)
        new_chat.reply(message)
        chats.append(new_chat)
    
    else:

        for actual_chat in chats:

            if actual_chat.get_chat_id() == chat_id:
                actual_chat.reply(message)
            else:
                new_chat = chat.chat(username, chat_id)
                new_chat.reply(message)
                chats.append(new_chat)



start_bot()