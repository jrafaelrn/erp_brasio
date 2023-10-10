from dotenv import load_dotenv
import os, psycopg2


def configure():
    load_dotenv()
    
    
class DbSales():
    
    
    def __init__(self):
        configure()
        self.DB_HOST = os.getenv('DATABASE_SALES_ADDRESS')
        self.DB_PORT = os.getenv('DATABASE_SALES_PORT')
        self.DB_USER = os.getenv('DATABASE_SALES_USER')
        self.DB_PASSWORD = os.getenv('DATABASE_SALES_PASSWORD')
        self.DB_NAME = 'db'
        
    
        
    def connect(self):
        
        try:            
            conecction_format = f'dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASSWORD} host={self.DB_HOST} port={self.DB_PORT}'
            self.connection = psycopg2.connect(conecction_format)
            print('Connected to database!')
            self.db = self.connection.cursor()
            return True            
        
        except Exception as e:
            print(f"Error while connecting: {e}")
            return False
    
    
    
    def execute(self, command, values):
            
        try:
            
            self.db.execute(command, values)
            
            try:
                self.bd_return = self.db.fetchall()
            except:
                self.bd_return = None
            
            print(f'Executed: [{command}] -> Result: {self.bd_return}')
            self.commit()
            return self.bd_return
        
        except Exception as e:
            print(f"Error while executing: {e}")
            return None
        
    
    
    def commit(self):
        
        try:
            self.connection.commit()
            return True
        
        except Exception as e:
            print(f"Error while commiting: {e}")
            return False
            
    
    
    def disconnect(self):
        self.db.close()
        self.connection.close()
        print('Disconnected from database!')



class DbSalesIfood():
       
    def insert_merchants(self, merchants):
        
        db = DbSales()
        db.connect()
        
        for merchant in merchants:
            
            print(f'Inserting merchant: {merchant}')
            
            
        db.disconnect()
            
            
            
    
    def insert_orders(self, orders):
        
        self.db = DbSales()
        self.db.connect()
        
        for order in orders:
            
            id_sale = self.insert_sale(order)[0]
            self.insert_transaction_base(id_sale, order)
    
        self.db.disconnect()
    
    
    
    
    def insert_sale(self, order):
        
        total = order['total']
        
        total_products = total['subTotal']
        total_shipping = total['deliveryFee']
        total_discount = total['benefits']
        total_fees = total['additionalFees']        
        order_amount = total['orderAmount']
        
        pre_paid_amount = order['payments']['prepaid']
        pending_amount = order['payments']['pending']
        
        db_table = 'api_transaction_sale'
        
        id_sale = self.db.execute(f'INSERT INTO {db_table} (total_products, total_shipping, total_discount, total_fees, order_amount, prepaid_amount, pending_amount) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id', (total_products, total_shipping, total_discount, total_fees, order_amount, pre_paid_amount, pending_amount))
        
        return id_sale[0]
    
    
    
    def get_source_id(self, order):
        
        db_table = 'integrations_integrationtransaction'
        merchant_id = order['merchant']['id']
        source_id = self.db.execute(f'SELECT id FROM {db_table} WHERE identifier = %s', (merchant_id,))
        return source_id[0][0]
        
    
        
    def insert_transaction_base(self, id_sale, order):
        
        db_table = 'api_transaction_transaction'
        
        created_at = order['createdAt']
        api_source_id = self.get_source_id(order)
        api_id = order['id']
        
        self.db.execute(f'INSERT INTO {db_table} (api_id, created_at, api_source_id, sale_id) VALUES (%s, %s, %s, %s)', (api_id, created_at, api_source_id, id_sale))
        
        
    
    
    def insert_transaction_client():
        pass
    
    def insert_transaction_delivery():
        pass