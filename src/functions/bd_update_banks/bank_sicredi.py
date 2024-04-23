import os, extract, bd, time, json, re
from datetime import datetime
import pandas as pd


acumulado = []
contador_acumulado = 0



##########################################
#               SICREDI                  #
##########################################

# Day: string with file name
def import_extrato_sicredi(extrato_file, account_name):

  global acumulado
  print(f'... Importing extrato {account_name} from File {extrato_file} ...')
  
  in_progress = False
  import_card = False
  balance_card = None
  date_payment_card = None

  for line in extrato_file.iterrows():
    
    # Try convert first column to date
    try:

      date_str = line[1][0]
      date_date = datetime.strptime(date_str, '%d/%m/%Y')  # Apenas para validacao da linha << Nao remover
      conta = account_name
      descricao = (line[1][1]).upper()
      doc, nome = extract.extract_cpf_cnpj_cliente_fornecedor_from_description(descricao)
      tipo = extract.extract_type(descricao, line[1][2])
      valor =  line[1][3]
      saldo = line[1][4]

      
      print(f'\nImporting date {line[1][0]}')
      print(f'\tConta: {conta}')
      print(f'\tDescricao: {descricao}')
      print(f'\tTipo: {tipo}')
      print(f'\tValor: {valor}')
      

      # Se encontrar uma fatura de cartao, procura o arquivo separado
      if descricao.find('DEB.CTA.FATURA') != -1:
          import_card = True
          balance_card = saldo
          date_payment_card = date_str
          continue
          

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

      import_accumulated_sicredi(DATA_JSON)

      in_progress = True
      

    except Exception as e:

      data = None
      print(f'Linha inválida: [0]:{line[1][0]} [1]:{line[1][1]} [2]:{line[1][2]} [3]:{line[1][3]} [4]:{line[1][4]}')
      print(f'Erro: {e}')
      
      
      if in_progress:
        
        # Se ocorrer um erro, é sinal de que todas as linhas "padrões"
        # já foram importadas. Então, se houver acumulado, envia para o BD
        if len(acumulado) > 0:
          bd.insert(acumulado)
          acumulado = []
          contador_acumulado = 0     
        
        return import_card, balance_card, date_payment_card

      if type(line[1][0]) == str:
        if line[1][0].find('Saldo da Conta') != -1:
          return None, None, None
    


# ACUMULA A CADA x LANÇAMENTOS, PARA ENVIAR DE UMA VEZ PARA O BD

def import_accumulated_sicredi(data_transaction):
  
  global acumulado
  global contador_acumulado
  max_acumulado = 5
  
  
  if contador_acumulado <= max_acumulado:
    
    contador_acumulado += 1
    acumulado.append(data_transaction)
    
  else:
    
    bd.insert(acumulado)
    acumulado = []
    contador_acumulado = 0







def import_card_sicredi(extrato_file, balance, date_payment_card, conta):

    print(f'...... Importing cartao Sicredi......\n')

    # If name is date
    #if type(extrato_file) == datetime:
      #name_file = extrato_file.strftime('%Y-%m')

    for line in extrato_file.iterrows():
      
      # Try convert first column to date
      try:
        
        linha = line[1][0]
        
        try:
          data = datetime.strptime(linha, '%d/%m/%Y')  # Apenas para validacao da linha
        except:
          data = datetime.strptime(str(linha), '%d/%m/%Y')  # Apenas para validacao da linha
        
        descricao = f'{line[1][1]} - {line[1][2]} - ({linha})'
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

        DATA = {}
        DATA['date_trx'] = date_payment_card
        DATA['account'] = conta
        DATA['original_description'] = descricao
        DATA['document'] = ''
        DATA['entity_bank'] = fornecedor
        DATA['type_trx'] = tipo
        DATA['value'] = valor
        DATA['balance'] = balance

        DATA_JSON = json.dumps(DATA)

        bd.insert(DATA_JSON)
        
      except Exception as e:
        msg = f'Linha inválida: {linha}\n\t error: {e}'
        print(msg)
        data = None





