from dotenv import load_dotenv
from .importer import ImporterApi_Interface
from retry import retry
import os, time

def configure():
    load_dotenv()
    

# STATIC VARIABLES
BASE_URL = 'https://merchant-api.ifood.com.br'
CLIENT_ID = os.getenv('IFOOD_CLIENT_ID')
CLIENT_SECRET = os.getenv('IFOOD_CLIENT_SECRET')


# Implements the "Importer" interface 
# to provide all the necessary methods 
# for downloading Rappi API data and saving it 
# in the database.

class ApiRappi(ImporterApi_Interface):
    
    def __init__(self):
        configure()
        self.api_name = 'rappi'
    
    
    def connect(self):
        print(f'Getting API KEY from {self.api_name}...')
        
    
    def download(self) -> bool:
        print(f'Downloading data from {self.api_name}...')
    
    
    def save_db(self) -> bool:
        print(f'Saving data from {self.api_name}...')
        
    
    @retry(delay=120, tries=1000)
    def start(self):
        
        try:
            
            while True:
                self.connect()
                self.download()
                self.save_db()
                time.sleep(7)
                
        except Exception as e:
            print(f'Error: {e}')
                
                

def start():
    rappi = ApiRappi()
    rappi.start()