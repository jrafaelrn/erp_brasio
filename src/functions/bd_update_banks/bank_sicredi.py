import os, extract, bd, time, json
from datetime import datetime


##########################################
#               SICREDI                  #
##########################################

# Day: string with file name
def import_extrato_sicredi(extrato_file):
    
    in_progress = False

    for line in extrato_file.iterrows():
      
      # Try convert first column to date
      try:
        
        print(f'DATE == [{line[1][0]}] -- TYPE: {type(line[1][0])}')
        date_str = str(line[1][0])
        conta = "SICREDI"
        print(f'DESCRICAO == [{line[1][1]}] -- TYPE: {type(line[1][1])}')
        descricao = line[1][1]
        doc, nome = extract.extract_cpf_cnpj_cliente_fornecedor_from_description(descricao)
        print(f'TIPO == [{line[1][2]}] -- TYPE: {type(line[1][2])}')
        tipo = extract.extract_type(descricao, line[1][2])
        print(f'VALOR == [{line[1][3]}] -- TYPE: {type(line[1][3])}')
        valor =  float(line[1][3])
        print(f'SALDO == [{line[1][4]}] -- TYPE: {type(line[1][4])}')
        saldo = float(line[1][4])

        
        print(f'\nImporting date {line[1][0]}')
        print(f'\tConta: {conta}')
        print(f'\tDescricao: {descricao}')
        print(f'\tTipo: {tipo}')
        print(f'\tValor: {valor}')
        

        # Se encontrar uma fatura de cartao, procura o arquivo separado
        if descricao.find('DEB.CTA.FATURA') != -1:
            continue
            #import_cartao_sicredi(data, saldo)
        else:
            DATA = {}
            DATA['date_trx'] = date_str
            DATA['account'] = conta
            DATA['original_description'] = descricao
            DATA['document'] = doc
            DATA['entity_bank'] = nome
            DATA['type_trx'] = tipo
            DATA['value'] = valor
            DATA['balance'] = saldo

            DATA_JSON = json.dumps(DATA)

            bd.insert(DATA_JSON)

            in_progress = True
            time.sleep(10)


      except Exception as e:

        data = None

        if in_progress:
          print(f'Linha inválida: {line[1][0]} - Error: {e}')
          return
    


def import_cartao_sicredi(name, saldo):

    print(f'\n\n... Importing cartao Sicredi...\n')

    # If name is date
    if type(name) == datetime:
      name_file = name.strftime('%Y-%m')

    # If not, import
    cartao_file = pd.read_excel(f'{path_drive_sicredi_cartao}/{name_file}.xls')


    for line in cartao_file.iterrows():
      
      # Try convert first column to date
      try:
        
        linha = line[1][0]
        data = datetime.strptime(linha, '%d/%m/%Y')  # Apenas para validacao da linha
        conta = "SICREDI"
        descricao = f'{line[1][1]} - {line[1][2]}'
        tipo = 'CARTAO CRED'
        valor = line[1][3]

        # Replace based on regex
        fornecedor = re.sub('\d+/\d+', '', line[1][1])

        # Check if valor is string
        if type(valor) == str:
          valor = valor.replace('.', '')
          valor = valor.replace(',', '.')
          valor = valor.replace('R$', '')
          valor = - float(valor)
        else:
          valor = - float(valor)

        if valor > 0:
          continue

        inserir_lancamento(name, conta, descricao, '', fornecedor, tipo, valor, saldo)
        
      except Exception as e:
        msg = f'Linha inválida: {linha}\n\t error: {e}'
        #print(msg)
        logging.warning(msg)
        data = None
      
    #Update name
    os.rename(f'{path_drive_sicredi_cartao}/{name_file}.xls', f'{path_drive_sicredi_cartao}/{name_file}-ok.xls')




