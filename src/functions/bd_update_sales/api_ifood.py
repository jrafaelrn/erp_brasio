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
        self.accessToken = None
    
    
    ###############################
    #           CONNECT           #
    ###############################
    
    def connect(self):
        print(f'Getting Access Token from {self.api_name}...')     
        
        if self.accessToken != None:
            return   
        
        URL = f'{BASE_URL}/authentication/v1.0/oauth/token'
        data={
            'clientId': self.CLIENT_ID,
            'clientSecret': self.CLIENT_SECRET,
            'grantType': 'client_credentials'
        }
        
        post = requests.post(URL, data=data)
        
        self.accessToken = post.json()['accessToken']
        self.configure_headers(self.accessToken)
        print(f'\tAccess Token obtained!')


    
    def configure_headers(self, access_token):
        auth = f'Bearer {self.accessToken}'
        self.headers = {"Authorization": auth}
    
    
    ###############################
    #          DOWNLOAD           #
    ###############################
    
    def download(self) -> bool:
        
        print(f'Downloading data from {self.api_name}...')
        
        # MERCHANTS
        self.merchants = self.download_merchants()
        #self.merchants_details = self.download_merchants_details(merchants)
        self.merchants_hash_downloaded = hashlib.md5(str(self.merchants).encode('utf-8')).hexdigest()
        
        # ORDERS
        self.orders = self.download_orders()
        self.orders_details = self.download_orders_details(self.orders)
        
        return True
    
    
    def download_merchants(self):
        
        print('\tDownloading merchants...')
        merchants = []
        URL = f'{BASE_URL}/merchant/v1.0/merchants'        
        post = requests.get(URL, headers=self.headers)
        
        return post.json()
    

    def download_merchants_details(self, merchants):
        
        print('\tDownloading merchants details...')
        URL = f'{BASE_URL}/merchant/v1.0/merchants/'
        merchants_details = []
        
        for merchant in merchants:
            post = requests.get(URL + merchant['id'], headers=self.headers)
            merchants_details.append(post.json())
            
        return merchants_details
            
        
    def download_orders(self):
        
        print('\tDownloading orders...')
        orders = []
        URL = f'{BASE_URL}/order/v1.0/events:polling'        
        post = requests.get(URL, headers=self.headers)
        
        if post.status_code != 200:
            print(f'\t\tStatus code: {post.status_code}')
            return None
        
        return post.json()
    
    
    def download_orders_details(self, orders):
        
        print('\tDownloading orders details...')
        orders_details = []
        URL = f'{BASE_URL}/order/v1.0/orders/'
        
        for order in orders:
            URL = f"{URL}{order['orderId']}"
            post = requests.get(URL, headers=self.headers)
            
            if post.status_code == 200:
                orders_details.append(post.json())
                
        return orders_details
    
    
    ###############################
    #             SAVE            #
    ###############################
    
    def save_db(self):
        
        print(f'Saving data from {self.api_name}...')
        
        db = DbSalesIfood()
        
        if self.merchants_hash_downloaded != self.merchants_hash_saved:
            db.insert_merchants(self.merchants)
            self.merchants_hash_saved = self.merchants_hash_downloaded
        
        if self.orders != None:
            db.insert_orders(self.orders)
        
    
    def send_acks():
        pass
    
    
    def send_ack(id):
        pass
    
    
    ###############################
    #           WATCHER           #
    ###############################
    
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