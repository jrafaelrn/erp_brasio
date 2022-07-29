from datetime import datetime
import extract, bd, json


##########################################
#               PAGBANK                  #
##########################################

def import_extrato_pagbank(extrato_file):

    for line in extrato_file.iterrows():     
        
        cod_transacao = line[1][0]
        data = datetime.strptime(line[1][1], '%d/%m/%Y')
        tipo_old = line[1][2]
        descricao = line[1][3]
        doc, nome = extract.extract_cpf_cnpj_cliente_fornecedor_from_description(tipo_old)
        tipo = extract.extract_type(descricao, tipo_old)
        valor = float(line[1][4].replace(',', '.'))
        conta = "PAGBANK"
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