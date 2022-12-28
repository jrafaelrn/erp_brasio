from datetime import datetime
import extract, bd, json, requests, time


##########################################
#               PAGBANK                  #
##########################################

def import_extrato_pagbank(extrato_file, conta):

    for line in extrato_file.iterrows():     
        
        cod_transacao = line[1][0]
        data = datetime.strptime(line[1][1], '%d/%m/%Y')
        tipo_old = (line[1][2]).upper()
        descricao = (line[1][3]).upper()
        doc, nome = extract.extract_cpf_cnpj_cliente_fornecedor_from_description(tipo_old)
        tipo = extract.extract_type(descricao, tipo_old)
        valor = float(line[1][4].replace(',', '.'))
        conta = conta.upper()
        descricao = f'{tipo_old} - {descricao}'

        DATA = {}
        DATA['date_trx'] = line[1][1]
        DATA['account'] = conta
        DATA['original_description'] = descricao
        DATA['document'] = doc
        DATA['entity_bank'] = nome
        DATA['type_trx'] = tipo
        DATA['value'] = valor
        DATA['balance'] = 0

        DATA_JSON = json.dumps(DATA)

        bd.insert(DATA_JSON)

        time.sleep(2)



# Day format = YYYY-MM-DD
def api_import(day):

    page_number = 1
    page_size = 1000
    edi_version = 2.01
    movement_type = [1, 2, 3]
    
    for mov_type in movement_type:
    
        url = f"https://edi.api.pagseguro.com.br/edi/v1/{edi_version}/movimentos?dataMovimento={day}&pageNumber={page_number}&pageSize={page_size}&tipoMovimento={mov_type}"
        headers = {"Accept": "application/json"}

        response = requests.get(url, headers=headers)

        print(f'GET: {url}')
        print(f'RESPONSE: {response.text}')



day = '2022-08-20'
api_import(day)
