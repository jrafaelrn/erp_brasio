from abc import abstractmethod


class ImporterApi():
    
    @abstractmethod
    def __init__(self, api):
        self.api = api
        print(f'Starting API to {self.api}...')
        
        
    @abstractmethod
    def connect(self):
        print(f'Connecting to {self.api}...')
        pass
    
    
    @abstractmethod
    def download(self):
        print(f'Downloading data from {self.api}...')
        pass
    
    
    @abstractmethod
    def save_db(self):
        print(f'Saving data from {self.api}...')
        pass
        
        
    
    