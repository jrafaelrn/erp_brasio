import base64
import sender

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


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

    # Configura o WebDriver do Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    for loja in urls:
        
        nome_loja = loja['loja']
        url = loja['url']
        msg = None
        
        try:
            driver.get(url)
            print(f"Acessando {nome_loja}: {url}")

            # Tenta encontrar o elemento que indica que a loja está fechada
            try:
                driver.find_element(By.XPATH, "//h2[contains(text(), 'Loja fechada')]")
                msg = f"'Loja Fechada': {nome_loja}."
            except:
                continue
            finally:
                driver.quit()
            
        except Exception as e:
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