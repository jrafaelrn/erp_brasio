import time, requests, json, os, chat


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
#             GLOBAL VARIABLES               #
##############################################

chats = []
API_KEY = get_key_from_os('TELEGRAM_API_KEY')
url_base = f'https://api.telegram.org/bot{API_KEY}/'



def start_bot():

    print('Starting bot...')
    print(f'API KEY: {API_KEY}')
    update_id = None
    query_id = None

    while True:
           
        try:

            atualizacao = get_messages_by_id(update_id)
            dados = atualizacao['result']

            if dados:
                for dado in dados:

                    update_id = dado['update_id']

                    try:
                        mensagem = str(dado['message']['text'])
                        chat_id = dado['message']['from']['id']
                        nome = dado['message']['chat']['first_name']
                        username = dado['message']['chat']['username']
                    except:
                        mensagem = str(dado['callback_query']['data'])
                        chat_id = dado['callback_query']['from']['id']
                        nome = dado['callback_query']['from']['first_name']
                        username = dado['callback_query']['from']['username']
                        query_id = dado['callback_query']['id']

                    msg = f'--->> Mensagem Recebida: [{mensagem}] - Chat ID: {chat_id} - Nome: {nome} - Update ID: {update_id} - Username: {username}'
                    print(msg)                     

                    if validate(username):
                        interact(username, chat_id, mensagem)
                    else:
                        chat.send_message('text', 'Usuário não autorizado!', chat_id)
                    
                    if query_id is not None:
                        answer_callback_query(query_id)
                        query_id = None
                        #keyboard_remove(chat_id)

        except Exception as e:
            print(f'Erro: {e}')
            continue

        time.sleep(1)

        #Print keep alive each 1 min
        if time.strftime("%S") == '00':
            print(f'\nKeep alive - Now: {time.strftime("%H:%M:%S")}')



def get_messages_by_id(update_id):

    link_request = f'{url_base}getUpdates'

    if update_id:
        update_id +=1
        link_request += f'?offset={update_id}'
    
    #print(f'\nLink request: {link_request}')  
    resp = requests.get(link_request)
    
    print(f'--->> UPDATE {update_id}: Response: {resp.status_code} - {resp.text} - Now: {time.strftime("%H:%M:%S")}')
    return json.loads(resp.content)




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


def answer_callback_query(query_id):

    method_url = 'answerCallbackQuery'
    payload = {
        'callback_query_id': query_id,
        'show_alert': True,
        'cache_time': 300
    }
    
    url = f'{url_base}{method_url}'

    resp = requests.post(url, data = payload)
    print(f'--> ASNWER CALLBACK - Response: {resp.status_code} - {resp.text}')



def keyboard_remove(chat_id):
    
    headers = {'Content-Type': 'application/json'}
    method_url = 'sendMessage'
    payload = {"remove_keyboard" : True}
    data = json.dumps(payload)

    link_resp = f'{url_base}{method_url}?chat_id={chat_id}&text=...&reply_markup={data}'
    resp = requests.get(link_resp, headers = headers, json = data)

    print(f'XXX - Remove Keyboard - Response: {resp.status_code} - {resp.text}')



start_bot()