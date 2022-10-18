from datetime import datetime, timedelta
import requests, os, json, time

USERNAME_PAGBANK: str
TOKEN_PAGBANK: str


def get_keys():

    global USERNAME_PAGBANK
    global TOKEN_PAGBANK

    USERNAME_PAGBANK = os.environ.get('USERNAME_PAGBANK')
    TOKEN_PAGBANK = os.environ.get('TOKEN_PAGBANK')



def get_data_by_date(date_mov: str):

    get_keys()

    url = f'https://edi.api.pagseguro.com.br/edi/v1/2.01/movimentos?dataMovimento={date_mov}&pageNumber=1&pageSize=100&tipoMovimento=2'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json'
    }

    r = requests.get(url, auth=(USERNAME_PAGBANK, TOKEN_PAGBANK), headers=headers)

    print(r.status_code)
    #print(r.text)

    return r.json()



def generate_file_json(name_file:str, movs: dict):
    
    path = 'G:/My Drive/Palhas Perandini/Financeiro/Extratos Bancarios/PagBank/Conta-API/'
    file_name = f'{path}{name_file}.json'

    movs_str = json.dumps(movs)

    with open(file_name, 'w') as f:
        f.write(movs_str)



def generate_file_csv(name_file:str, movs: dict):

    path = 'G:/My Drive/Palhas Perandini/Financeiro/Extratos Bancarios/PagBank/Conta/'
    file_name = f'{path}{name_file}.csv'


    with open(file_name, 'w') as f:

        f.write('CODIGO DA TRANSACAO;DATA;TIPO;DESCRICAO;VALOR')

        for mov in movs:
            
            cod_transacao = mov['codigo_transacao']
            data = mov['data_movimentacao']
            tipo = mov['tipo_transacao']
            descricao = mov['codigo_venda']
            valor = mov['valor_liquido_transacao']

            data_ptbr = datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m/%Y')

            if tipo == '1':
                continue

            f.write(f'\n{cod_transacao};{data_ptbr};{tipo};{descricao};{valor}')



def download(date_download: str):

    print(f'--->> Downloading {date_download}...')

    mov_details = get_data_by_date(date_download)['detalhes']

    generate_file_json(date_download, mov_details)
    generate_file_csv(date_download, mov_details)

    #print(mov_details)



if __name__ == '__main__':
    
    start_date = datetime(2022, 8, 1)
    end_date = datetime(2022, 9, 8)
    
    for n in range(int ((end_date - start_date).days)):
        date_download = start_date + timedelta(n)
        download(date_download.strftime('%Y-%m-%d'))
        time.sleep(1)
