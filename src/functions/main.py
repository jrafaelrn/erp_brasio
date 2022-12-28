#from .check_sales import *

import os

ACTUAL_FOLDER = os.getcwd()
ACTUAL_FILE_REQUIREMENTS = os.path.join(ACTUAL_FOLDER, "src\\functions\\", "requirements.txt")



def create_requirements():
    
    requirements = get_requirements_list()
    delete_old_requirements()
    create_new_requirements(requirements)
        
    print("File 'requirements.txt' created successfully!")



def get_requirements_list():
    
    folders = os.listdir("src/functions")
    list_requirements = []
    
    for folder in folders:
        
        folder = os.path.join(ACTUAL_FOLDER, "src\\functions", folder)
        
        if os.path.isdir(folder):            
            if "requirements.txt" in os.listdir(folder):
                
                path = os.path.join(folder, "requirements.txt")
                
                with open(path) as f:
                    list_requirements.extend(f.read().splitlines())
                    
    
    # Remove duplicates
    list_requirements = list(dict.fromkeys(list_requirements))
    
    return list_requirements


def delete_old_requirements():
    
    if os.path.exists(ACTUAL_FILE_REQUIREMENTS):
        os.remove(ACTUAL_FILE_REQUIREMENTS)
    

def create_new_requirements(requirements):
    
    # Write the content of the list to the file
    with open(ACTUAL_FILE_REQUIREMENTS, "w") as f:
        for requirement in requirements:
            f.write(requirement + "\n")
        f.close()
    

create_requirements()