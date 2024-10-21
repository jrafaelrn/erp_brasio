import base64
import requests
import sender


def check_if_alive():

    # URL que será acessada
    urls = [
        {'loja': 'Vianelo',
        'url': 'https://www.ifood.com.br/delivery/jundiai-sp/palhadini-palha-italiana-doce-e-salgado-vila-argos-nova/6a608776-d22b-4784-ba02-587446fc3a01'
        },
        {'loja': 'Medeiros',
        'url': 'https://www.ifood.com.br/delivery/jundiai-sp/palhadini-palha-italiana---doces-medeiros/ff1f48c4-3f94-448a-bdcf-c9ba07333fdd'
        }
    ]


    for loja in urls:
        
        nome_loja = loja['loja']
        url = loja['url']
        msg = None
        
        try:
            # Faz a requisição GET para a URL
            response = requests.get(url)

            # Verifica se a requisição foi bem-sucedida (código 200)
            if response.status_code == 200:
                # Verifica se o texto "Loja Fechada" está presente no conteúdo da página
                if "Loja Fechada" in response.text:
                    msg = f"'Loja Fechada': {loja['loja']}."
                else:
                    msg = f"'Loja Aberta': {loja['loja']}."
            else:
                msg = f"Erro ao acessar a página da loja {loja['loja']}. Código de status: {response.status_code}"

        except requests.exceptions.RequestException as e:
            msg = f"Ocorreu um erro na requisição para a loja {loja['loja']}: {e}"

        # Envia a mensagem para o Telegram
        sender.send_message(msg, '572312369')


#################################
#   Call from Cloud Functions   #
#################################

def check(event, context):

    if type(event) != str:
        payload = base64.b64decode(event['data']).decode('utf-8')
    else:
        payload = event

    response = None

    print(f'Payload: {payload}')
    
    try:
        check_if_alive()    
        response = {"return": "ok"}
    except:
        response = {"return": "error"}

    print(f'Response: {response}')
    return response


if __name__ == '__main__':
    check_if_alive()
    print('Check Ifood Alive sucecesfully!')