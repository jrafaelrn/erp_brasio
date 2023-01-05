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
            
            print(f'Executed: {command} with values: {values} -> Result: {self.bd_return}')
            return self.bd_return
        
        except Exception as e:
            print(f"Error while executing: {e}")
            return None
        
    
    
    def commit(self):
        
        try:
            self.db.commit()
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
        
        db = DbSales()
        db.connect()
        
        for order in orders:
            
            print(f'Inserting order: {order}')
    
        db.disconnect()