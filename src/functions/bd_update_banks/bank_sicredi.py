import io
import json
import logging
import os
import pandas as pd
import re
import time

from datetime import datetime
from dataclasses import dataclass
logger = logging.getLogger()

from bank import Bank

logger = logging.getLogger()


@dataclass
class BankSicredi(Bank):
  
  
  def import_account(self):

    logger.info('... Importing extrato %s from File %s ...', self.bank_name, self.file_name)

    for line in self.file_data.itertuples(index=False):
      
      # Try convert first column to date
      try:

        date_str = line[0]
        date_date = datetime.strptime(date_str, '%d/%m/%Y')  # Apenas para validacao da linha << Nao remover
        descricao = (line[1]).upper()
        pre_type = line[2]
        valor =  line[3]
        saldo = line[4]
        

        # Se encontrar uma fatura de cartao, procura o arquivo separado
        if (descricao.find('DEB.CTA.FATURA') != -1) or (descricao.find('LIQUIDACAO BOLETO SICREDI 82527557000140 SICREDI') != -1):
            self.card_transactions_to_import = True
            self.balance_card = saldo
            self.date_payment_card = date_str
            
            continue
        
        self.create_transaction(
          date_trx=date_date,
          original_description=descricao,
          pre_type=pre_type,
          value=valor,
          balance=saldo,
        )

      except Exception as e:

        logger.warning('Linha inválida: %s || Error: %s', line, e)            
        
        if self.import_account_progress:
          
          # Se ocorrer um erro, é sinal de que todas as linhas "padrões"
          # já foram importadas. Então, se houver acumulado, envia para o BD
          if len(self.transactions) > 0:
            self.flush_transactions()
          
          return 

        try:
          if type(line[1][0]) == str:
            if line[1][0].find('Saldo da Conta') != -1:
              return
        except:
          pass  
      

  
  def check_card_file(self):
      
      # Check if card file exists
      if self.card_transactions_to_import:
          
          logging.info('Checking if card file exists...')

          card_path_file_filter = f'{self.account_name}/CARTAO-CSV/'
          card_name_file_filter = datetime.strptime(self.date_payment_card, '%d/%m/%Y').strftime('%Y-%m') + '-import.xls'
          file_name_card, file_id_card = check_if_file_exists(card_path_file_filter, card_name_file_filter)

          if file_name_card is False:
              logging.error(f'Card file not found! -- Card Path File Filter: {card_path_file_filter} -- Card Name File Filter: {card_name_file_filter}')
              self.rename_file('error')
              return None, None, None, None


  def update_file_name_after_import(self, new_sufix='ok'):
      # Rename file
      if self.google_drive.rename_file(self.file_id, self.file_name, new_sufix):
          logging.info('File renamed!')
      else:
          logging.error('ERROR - File not renamed!')   
          raise Exception('ERROR - File not renamed!')

      

  def update_bd_from_sicredi_card(self, file_id_card, balance_card, date_payment_card, card_name_file_filter):
      
      logging.info(f'Starting update BD from Sicredi Card...\nFile Card ID: {file_id_card}\nBalance Card: {balance_card}\nDate Payment Card: {date_payment_card}\nCard Name File Filter: {card_name_file_filter}')

      global account_name
      
      file_excel = get_file(file_id_card)

      if file_excel is None:
          logging.error('No file found!')
          return
      
      df = pd.read_excel(io.BytesIO(file_excel))            
      self.import_card_sicredi(df, balance_card, date_payment_card, account_name)

      # Rename file
      if rename_file(file_id_card, card_name_file_filter, 'ok'):
          logging.info('File renamed!')
      else:
          logging.error('ERROR - File not renamed!')  
          raise Exception('ERROR - File not renamed!')




  def import_card(self, extrato_file, balance, date_payment_card, conta):

    logger.info(f'...... Importing cartao Sicredi......\n')

    for line in extrato_file.iterrows():
      
      # Try convert first column to date
      try:
        
        linha = line[1][0]
        
        try:
          data = datetime.strptime(linha, '%d/%m/%Y')  # Apenas para validacao da linha
        except:
          data = datetime.strptime(str(linha), '%d/%m/%Y')  # Apenas para validacao da linha
        
        descricao = f'{line[1][1]} - {line[1][2]} - ({linha})'
        descricao = descricao.upper()
        tipo = 'CARTAO CRED'
        valor = line[1][3]

        # Replace based on regex
        fornecedor = re.sub(r'\d+/\d+', '', line[1][1])

        # Check if valor is string
        if type(valor) == str:
          valor = valor.replace('.', '')
          valor = valor.replace(',', '.')
          valor = valor.replace('R$', '')
          valor = - float(valor)
        else:
          valor = - float(valor)

        # If values is positive and payment, ignore
        if valor > 0 and (descricao.find('PAGAMENTO') != -1 or descricao.find('QUITACAO') != -1 or descricao.find('PAG FAT DEB') != -1):
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

        #bd.insert([DATA_JSON])
        self.import_accumulated_sicredi(DATA_JSON)
        
      except Exception as e:
        msg = f'Linha inválida: {linha}\n\t error: {e}'
        print(msg)
        data = None
        
    self.import_accumulated_sicredi(DATA_JSON, True)





