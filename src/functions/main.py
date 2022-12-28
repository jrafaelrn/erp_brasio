from multiprocessing import Pool

from requirements_generator import install_requirements
from .bd_update_sales import *


install_requirements()

#with Pool() as p:
# results = p.imap_unordered(bd_update_sales)