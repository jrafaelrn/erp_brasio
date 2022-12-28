class connectAPI:
    
    def __init__(self, api_name):
        print(f'Starting API to {api_name}')
        self.api_name = api_name
        
        
    def send_email(self):
        print(f'Sending email to {self.api_name}')
        pass
    

    def connect(self):
        print(f'Connecting to {self.api_name}')
        pass
    
    
    def run(self):
        
        try:
            print(f'Running {self.api_name}')
            self.send_email()
            self.connect()
            print(f'Finished sucessfully {self.api_name}!')
            return True
        except:
            print(f'Error running {self.api_name}')
            return False
        
    