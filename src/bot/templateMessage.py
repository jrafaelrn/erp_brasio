import math
import os


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



def msg_categorys_erp():

    titulo = 'Categorias\n'
    categorias = ''
    contador = 0

    bd = open_bd_consumer_categoria_fornecedor('Categoria')

    for line in bd.iterrows():
        contador += 1
        categoria = line[1][2]
        categorias += f'{contador} - {categoria} {os.linesep}'

    return titulo + categorias


def mensagem_fornecedores():
            
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


def mensagem_sucesso(categoria, cliente_fornecedor):

    return f'''
    Pendência preenchida com sucesso! \o/
    Categoria: {categoria}
    Cliente/Fornecedor: {cliente_fornecedor}
    '''