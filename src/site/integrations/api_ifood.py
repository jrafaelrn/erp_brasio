from importer import *

class APIIfood(ImporterApi):
    
    ifood = ImporterApi('ifood')
    api_name = 'ifood'
    
    def connect(self):
        print('Getting API KEY')