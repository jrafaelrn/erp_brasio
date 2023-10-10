from multiprocessing import Pool

from requirements_generator import install_requirements
from bd_update_sales.apis import run


if __name__ == '__main__':
    print(f'Starting system at {__name__}...')
    install_requirements()
    run()
