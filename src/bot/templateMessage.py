import math, os, cloudFunctions


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


def msg_categorys_erp():

    titulo = 'Categorias\n'
    categorias = ''
    contador = 0

    #bd = open_bd_consumer_categoria_fornecedor('Categoria')

    for line in bd.iterrows():
        contador += 1
        categoria = line[1][2]
        categorias += f'{contador} - {categoria} {os.linesep}'

    return titulo + categorias



def msg_suppliers_erp():
            
    fornecedores = []
    contador = 0

    bd = open_bd_consumer_categoria_fornecedor('Descrição / Fornecedor')

    for line in bd.iterrows():
        
        fornecedor = line[1]['Descrição / Fornecedor']

        if fornecedor == None or fornecedor == '':
            continue
        else:
            fornecedor = fornecedor.replace('&', 'e')
            contador += 1

        fornecedores.append(f'{contador} - {fornecedor} {os.linesep}')   
    
    # Remove last one
    fornecedores.pop()

    return fornecedores








def msg_success(category, supplier, description):

    return f'''
    Pendência preenchida com sucesso! \o/
    Categoria: {category}
    Cliente/Fornecedor: {supplier}
    Descrição: {description}
    '''