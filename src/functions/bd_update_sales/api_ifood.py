from dotenv import load_dotenv
from importer import ImporterApi_Interface
from retry import retry
from bd_sales import DbSalesIfood
import os, time, requests, hashlib

def configure():
    load_dotenv()
    

# STATIC VARIABLES
BASE_URL = 'https://merchant-api.ifood.com.br'


# Implements the "Importer" interface 
# to provide all the necessary methods 
# for downloading Ifood API data and saving it 
# in the database.

class ApiIfood(ImporterApi_Interface):
    
    def __init__(self):
        configure()
        self.CLIENT_ID = os.getenv('IFOOD_CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('IFOOD_CLIENT_SECRET')
        self.api_name = 'ifood'
    
    
    def connect(self):
        print(f'Getting Access Token from {self.api_name}...')        
        
        URL = f'{BASE_URL}/authentication/v1.0/oauth/token'
        data={
            'clientId': self.CLIENT_ID,
            'clientSecret': self.CLIENT_SECRET,
            'grantType': 'client_credentials'
        }
        
        post = requests.post(URL, data=data)
        
        self.accessToken = post.json()['accessToken']

        
    
    def download(self) -> bool:
        
        print(f'Downloading data from {self.api_name}...')
        
        # MERCHANTS
        self.merchants = self.download_merchants()
        self.merchants_hash_downloaded = hashlib.md5(str(self.merchants).encode('utf-8')).hexdigest()
        
        # ORDERS
        self.orders = self.download_orders()
        
        return True
    
    
    def download_merchants(self):
        
        merchants = []
        URL = f'{BASE_URL}/merchant/v1.0/merchants'
        auth = f'Bearer {self.accessToken}'
        headers = {"Authorization": auth}
        
        post = requests.get(URL, headers=headers)
        
        return post.json()
            
        
    def download_orders(self):
        
        orders = []
        URL = f'{BASE_URL}/order/v1.0/events:polling'
        auth = f'Bearer {self.accessToken}'
        headers = {"Authorization": auth}
        
        post = requests.get(URL, headers=headers)
        
        if post.status_code != 200:
            print(f'Status code: {post.status_code}')
            return None
        
        return post.json()
    
    
    
    def save_db(self):
        print(f'Saving data from {self.api_name}...')
        
        db = DbSalesIfood()
        
        if self.merchants_hash_downloaded != self.merchants_hash_saved:
            db.insert_merchants(self.merchants)
            self.merchants_hash_saved = self.merchants_hash_downloaded
            
        db.insert_orders(self.orders)
        
        
        
    
    @retry(delay=10, tries=1000)
    def start(self):
        
        try:
            
            self.connect()
            self.merchants_hash_saved = None
            
            while True:
                if self.download():
                    self.save_db()
                    
                time.sleep(5)
                
        except Exception as e:
            print(f'Error: {e}')
            raise e
                
                

def start():
    ifood = ApiIfood()
    ifood.start()