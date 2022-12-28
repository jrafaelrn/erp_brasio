#from .check_sales import *

import os


try:
    ACTUAL_FOLDER = os.getcwd() + "\\src\\functions"
    ACTUAL_FOLDERS_REQUIREMENTS = os.listdir("src/functions")
    ACTUAL_FILE_REQUIREMENTS = os.path.join(ACTUAL_FOLDER, "requirements.txt")
    os.path.exists(ACTUAL_FOLDER)
except FileNotFoundError:
    ACTUAL_FOLDER = os.getcwd()
    ACTUAL_FILE_REQUIREMENTS = os.path.join(ACTUAL_FOLDER, "requirements.txt")
    ACTUAL_FOLDERS_REQUIREMENTS = os.listdir()


def create_requirements():
    
    requirements = get_requirements_list()
    delete_old_requirements()
    create_new_requirements(requirements)
        
    print("File 'requirements.txt' created successfully!")



def get_requirements_list():
    
    list_requirements = []
    
    for folder in ACTUAL_FOLDERS_REQUIREMENTS:
        
        folder = os.path.join(ACTUAL_FOLDER, folder)
        
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
    
    

def install_requirements():
    
    create_requirements()
    os.system(f"pip install -r {ACTUAL_FILE_REQUIREMENTS}")
    print("Requirements installed successfully!")
    

