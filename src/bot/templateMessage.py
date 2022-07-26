import math, os, cloudFunctions

categories = []
entities = []

def msg_menu():
    
    return '''
    Menu Principal
    1 - Verificar pendencias
    2 - Vendas/Meta do dia
    3 - Entradas no mês
    4 - Saídas no mês
    5 - Sair
    '''



def msg_pendency(date, account, description, value):

    valor = f'{value:.2f}'
    valor = valor.replace('.', ',')

    return f'''
    Data:  {date}
    Conta:  {account}
    Descrição:  {description} 
    Valor:  R$  {valor}
    '''


def msg_make_question(line):

    date = line['DATA']
    account = line['CONTA']
    description = line['DESCRICAO_ORIGINAL']
    value = line['VALOR']

    pendency = msg_pendency(date, account, description, value)
    
    return pendency


def msg_categories_erp():

    if len(categories) == 0 or len(entities) == 0:
        get_erp_data()

    return categories



def msg_suppliers_erp():
            
    suppliers = []

    for entity in entities:
        entity = entity.replace('&', 'e')
        suppliers.append(entity)

    suppliers.append('Novo fornecedor')
    
    return suppliers



def get_erp_data():

    global categories
    global entities

    # Get data
    filters = ['Categoria', 'Descrição / Fornecedor']
    FUNCTION_NAME = 'function-erp-classes'
    DATA = {"filters": filters}
    classes = cloudFunctions.cloud_function(FUNCTION_NAME, DATA)

    categories = classes[filters[0]]
    entities = classes[filters[1]]








def msg_success(category, supplier, description):

    return f'''
    Pendência preenchida com sucesso! \o/
    Categoria: {category}
    Cliente/Fornecedor: {supplier}
    Descrição: {description}
    '''