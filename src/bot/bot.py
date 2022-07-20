import time, requests, json


def start_bot():

    print('Starting bot...')

    while True:
           
            atualizacao = self.msg.get_messages_by_id(self.update_id)
            dados = atualizacao['result']

            if dados:

                for dado in dados:

                    try:
                        update_id = dado['update_id']
                        chat_id = dado['message']['from']['id']
                        mensagem = str(dado['message']['text'])
                        nome = dado['message']['chat']['first_name']
                        username = dado['message']['chat']['username']
                        msg = f'Mensagem Recebida: [{mensagem}] - Chat ID: {self.chat_id} - Nome: {nome} - Update ID: {self.update_id} - Username: {username}'
                        print(msg)                     


                        if security.validate(username):
                            interagir(mensagem)
                        else:
                            msg.enviarMensagem('Usuário não autorizado!', chat_id)

                    except Exception as e:
                        print(f'\nErro: {e}')
                        continue

            time.sleep(3)



def get_messages_by_id(self, update_id):

    link_request = f'{self.url_base}getUpdates?timeout=50'
    if update_id:
        link_request += f'&offset={update_id + 1}'
    resp = requests.get(link_request)
    return json.loads(resp.content)