from tkinter import E
from bank import Bank
from datetime import datetime
from dataclasses import dataclass

import json
import logging
import re

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
            self.date_payment_card = date_date
            
            continue
        
        transaction = self.create_transaction(
          date_trx=date_date,
          original_description=descricao,
          pre_type=pre_type,
          value=valor,
          balance=saldo,
        )

        self.add_transaction(transaction)

      except Exception as e:

        logger.warning('Linha inválida: %s || Error: %s', line, e)            
        
        if self.import_account_progress:
          
          # Se ocorrer um erro, é sinal de que todas as linhas "padrões"
          # já foram importadas. Então, se houver acumulado, envia para o BD
          if len(self.transactions) > 0:
            self.flush_transactions()
          
          return 

        try:
          if type(line[1][0]) is str:
            if line[1][0].find('Saldo da Conta') != -1:
              return
        except Exception as e2:
          logger.error('Erro ao analisar linha inválida: %s || Error: %s', line, e2)
      

  
  def update_file_name_after_import(self, new_sufix='ok'):
      # Rename file
      if self.google_drive.rename_file(self.file_id, self.file_name, new_sufix):
          logging.info('File renamed!')
      else:
          logging.error('ERROR - File not renamed!')   
          raise Exception('ERROR - File not renamed!')



  def import_card(self):

    logger.info(f'...... Importing SICREDI card file: {self.file_name} ......')
    linha = 'START'

    for line in self.file_data.itertuples(index=False):
      
      # Try convert first column to date
      try:
        
        linha = line[0]
        
        try:
          data = datetime.strptime(linha, '%d/%m/%Y')  # Apenas para validacao da linha
        except Exception as e:
          data = datetime.strptime(str(linha), '%d/%m/%Y')  # Apenas para validacao da linha
        
        descricao = f'{line[1]} - {line[2]} - ({linha})'
        descricao = descricao.upper()
        tipo = 'CARTAO CRED'
        valor = line[3]

        # Replace based on regex
        fornecedor = re.sub(r'\d+/\d+', '', line[1])

        # Check if valor is string
        if type(valor) is str:
          valor = valor.replace('.', '')
          valor = valor.replace(',', '.')
          valor = valor.replace('R$', '')
          valor = - float(valor)
        else:
          valor = - float(valor)

        # If values is positive and payment, ignore
        if valor > 0 and (descricao.find('PAGAMENTO') != -1 or descricao.find('QUITACAO') != -1 or descricao.find('PAG FAT DEB') != -1):
          continue

        transaction = self.create_transaction(
          date_trx=self.date_payment_card,
          original_description=descricao,
          pre_type=tipo,
          value=valor,
          balance=self.balance_card,
        )

        transaction.entity_name = fornecedor
        transaction.type = tipo

        self.add_transaction(transaction)

        
      except Exception as e:
        logger.debug(f'Linha inválida: {linha}\n\t error: {e}')
        





