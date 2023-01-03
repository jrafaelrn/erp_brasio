from abc import abstractmethod, ABC

# Interface that should be used for all APIs.
class ImporterApi_Interface(ABC):
    
    @abstractmethod
    def __init__(self, api):
        self.api = api
        print(f'Starting API to {self.api}...')
        pass
        
        
    @abstractmethod
    def connect(self) -> bool:
        print(f'Connecting to {self.api}...')
        pass
    
    
    @abstractmethod
    def download(self) -> bool:
        print(f'Downloading data from {self.api}...')
        pass
    
    
    @abstractmethod
    def save_db(self) -> bool:
        print(f'Saving data from {self.api}...')
        pass
        
        
    
    