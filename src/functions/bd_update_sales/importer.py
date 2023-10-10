from abc import abstractmethod, ABC

# Interface that should be used for all APIs.
class ImporterApi_Interface(ABC):
    
    @abstractmethod
    def __init__(self):
        pass
        
        
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    
    @abstractmethod
    def download(self) -> bool:
        pass
    
    
    @abstractmethod
    def save_db(self) -> bool:
        pass
        
        
    
    