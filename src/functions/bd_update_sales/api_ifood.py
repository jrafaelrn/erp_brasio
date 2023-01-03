from dotenv import load_dotenv
from .importer import ImporterApi_Interface
from retry import retry
import os, time, requests

def configure():
    load_dotenv()
    

# STATIC VARIABLES
BASE_URL = 'https://merchant-api.ifood.com.br'


# Implements the "Importer" interface 
# to provide all the necessary methods 
# for downloading Ifood API data and saving it 
# in the database.

class ApiIfood(ImporterApi_Interface):
    
    accessToken = None
    
    def __init__(self):
        configure()
        self.CLIENT_ID = os.getenv('IFOOD_CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('IFOOD_CLIENT_SECRET')
        self.api_name = 'ifood'
    
    
    def connect(self):
        print('Getting Access Token from {self.api_name}...')        
        
        URL = f'{BASE_URL}/authentication/v1.0/ouath/token'
        
        post = requests.post(URL, data={
            'clientId': self.CLIENT_ID,
            'clientSecret': self.CLIENT_SECRET,
            'grant_type': 'client_credentials'
        })
        
        print(post)
        accessToken = post.json()['accessToken']
        print(f'Access Token: {accessToken}')
        
    
    def download(self) -> bool:
        print(f'Downloading data from {self.api_name}...')
    
    
    def save_db(self) -> bool:
        print(f'Saving data from {self.api_name}...')
        
    
    @retry(delay=10, tries=1000)
    def start(self):
        
        try:
            
            while True:
                self.connect()
                self.download()
                self.save_db()
                time.sleep(5)
                
        except Exception as e:
            print(f'Error: {e}')
            raise e
                
                

def start():
    ifood = ApiIfood()
    ifood.start()