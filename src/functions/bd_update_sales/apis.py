from multiprocessing import Pool, Process
import importlib, multiprocessing

def get_apis_list():

    API_BASE_LIST = ['ifood']
    modules_name = lambda x : f'api_{x}'
    MODULES_API_LIST = list(map(modules_name, API_BASE_LIST))
    return MODULES_API_LIST

    
def send_email():
    pass
    

def run():
    
    modules = get_apis_list()
    procs = []

    for module in modules:
        
        print(f'Importing module: {module}')
        mod = importlib.import_module(f'bd_update_sales.{module}')
        
        # Creating process
        proc = multiprocessing.Process(target=mod.start)
        procs.append(proc)

        
    # Starting all processes
    for proc in procs:        
        proc.start()

    print(f'All modules started...: {modules}')
    
    for proc in procs:
        proc.join()
                        
            