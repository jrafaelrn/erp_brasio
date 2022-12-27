from importer import *
from dotenv import load_dotenv

def configure():
    load_dotenv()

class APIIfood(ImporterApi):
    
    ifood = ImporterApi('ifood')
    api_name = 'ifood'
    
    def __init__(self, api):
        configure()
    
    def connect(self):
        print('Getting API KEY')