from multiprocessing import Pool, Process
import importlib, multiprocessing


def get_apis_list(apis_name):

    modules_name = lambda x : f'api_{x}'
    modules_api_list = list(map(modules_name, apis_name))
    return modules_api_list



def transform_module_into_processes(modules):

    procs = []

    for module in modules:
        
        print(f'Importing module: {module}')
        mod = importlib.import_module(module)
        
        # Creating process
        proc = multiprocessing.Process(target=mod.start)
        procs.append(proc)
        
    return procs



def run_processes(procs):
    
    # Starting all processes
    for proc in procs:        
        proc.start()

    
    for proc in procs:
        proc.join()
                        

    
    
def send_email():
    pass
    
    

def run():
    
    # Gets the list of all modules(files) starting with "api_ + base list"
    API_BASE_LIST = ['ifood']
    modules = get_apis_list(API_BASE_LIST)
    
    # Turns all modules into processes, with the "start" method to run
    procs = transform_module_into_processes(modules)
    
    run_processes(procs)
    
        


if __name__ == '__main__':
    run()            