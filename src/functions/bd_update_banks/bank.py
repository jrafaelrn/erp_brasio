from datetime import date
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from transaction import Transaction

import bd
import io
import json
import logging
import pandas as pd
import re


logger = logging.getLogger()



@dataclass
class Bank(ABC):
    
    # Bank details
    bank_name: str
    file_name: str
    file_id: str
    file_path: str
    transactions: List[Transaction] = field(default_factory=list)
    
    # Card details
    is_card_file: bool = False
    card_file_name: str = None
    card_transactions_to_import: bool = False
    balance_card: float = 0.0
    date_payment_card: date = None

    # Import progress flags
    import_account_progress: bool = False
    import_card_progress: bool = False
    MAXIMUM_TRANSACTIONS_ACCUMULATED: int = 20
    counter: int = 0


    def __post_init__(self):
        
        # Check if file is card file
        # If file path contains 'CARTAO', it's a card file. 
        # Then, set is_card_file to True and 
        # extract the date from file name to set card_file_name (format: YYYY-MM-DD)
        
        if self.file_path.upper().find('CARTAO') != -1:
            self.is_card_file = True
            match = re.search(r'(\d{4})-(\d{2})-(\d{2})', self.file_name)
            if match:
                self.card_file_name = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                

    @abstractmethod
    def import_account(self):
        pass
    
    @abstractmethod
    def import_card(self):
        pass
    
    
    
    def download_file(self):
        
        file_excel = self.google_drive.get_file(self.file_id)

        if file_excel is None:
            logger.error('No file found!')
            raise Exception('No file found!')
                
        df = pd.read_excel(io.BytesIO(file_excel))
        return df
    
    
    
    def import_bank(self, google_drive, card_details=None):
        
        self.google_drive = google_drive
        self.file_data = self.download_file()

        if self.is_card_file:
            self.date_payment_card = card_details['date_payment']
            self.balance_card = card_details['balance']
            self.import_card()
            logging.info('File card imported!')        
        else:
            self.import_account()
            logging.info('File account imported!')        
            
        # Check if has card to import
        if self.card_transactions_to_import:
            card_details = {}
            card_details['date_payment'] = self.date_payment_card            
            card_details['balance'] = self.balance_card
            return True, card_details
        else:       
            return True, False
        
        return False, False
    
    
    
    def create_transaction(self, date_trx, original_description, pre_type, value, balance):
        transaction = Transaction(
            transaction_date=date_trx,
            description=original_description,
            pre_type=pre_type,
            value=value,
            balance_after=balance
        )
        return transaction


    
    def add_transaction(self, transaction: Transaction):
        
        self.transactions.append(transaction)
        self.counter += 1
        self.import_account_progress = True
        logger.info(f'Added transaction to queue... [{len(self.transactions)}/{self.MAXIMUM_TRANSACTIONS_ACCUMULATED}]')
        
        #Check if maximum accumulated reached
        if len(self.transactions) >= self.MAXIMUM_TRANSACTIONS_ACCUMULATED:
            self.flush_transactions()
            
            
            
    def flush_transactions(self):
        
        logger.info(f'Flushing {len(self.transactions)} transactions to BD...')
        DATA = []
        
        for transaction in self.transactions:
            
            TRX = {}
            TRX['transaction_date'] = transaction.transaction_date.strftime('%d/%m/%Y')
            TRX['account'] = self.bank_name
            TRX['original_description'] = transaction.description
            TRX['value'] = transaction.value
            TRX['balance'] = transaction.balance_after
            TRX['transaction_type'] = transaction.type
            TRX['entity_document'] = transaction.entity_document
            TRX['entity_name'] = transaction.entity_name
            
            # Acumula em DATA
            DATA.append(json.dumps(TRX))
        
        #bd.insert(DATA)
        self.transactions.clear()
        self.import_account_progress = False
    
    
    
    def check_folder_path(folder_to_check: str):
    
        file_path_filter = ['Sicredi/Conta/','Sicredi-Bruna/Conta-CSV/', 'Sicredi-Bruna-0002/Conta-CSV/'] 
        
        for path_filter in file_path_filter:
            if folder_to_check.upper().find(path_filter.upper()) != -1:
                return True
            
            
        file_path_filter = r"(.)*PagBank(.)*/Conta/"
        #conta_filter = r"Extratos Bancarios/(.*)/Conta"

        filter = re.match(file_path_filter, folder_to_check)
        if filter:
            return True
            
        return False