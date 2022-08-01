from turtle import update
import pyautogui, time, bd
import pandas as pd
from pynput.keyboard import Controller
from bd import *



class Consumer(object):

    def abrir_contas_pagar(self):

        time.sleep(10)
        print('Abrindo contas a pagar')
        pyautogui.hotkey('alt', 'f')
        time.sleep(3)
        pyautogui.hotkey('c', 'o')
        time.sleep(3)
        
        #Click center of screen
        pyautogui.click(x=pyautogui.size()[0]/2, y=pyautogui.size()[1]/2)
        time.sleep(3)
        pyautogui.press('f2')

        self.lancar_todos()



    def lancar_todos(self):

        bd_bot = bd.open_bd_bank()
        df_bd = pd.DataFrame(bd_bot.get_all_records(value_render_option='UNFORMATTED_VALUE'))

        for row in df_bd.iterrows():

            status_consumer = row[1]['STATUS_ERP']
            valor = float(row[1]['VALOR'])

            #if status_consumer != 'Pago' and valor < 0:
            if status_consumer == 'Novo' and valor < 0:

                
                grupo = row[1]['CATEGORY_ERP']
                fornecedor = row[1]['ENTITY_ERP']
                descricao = row[1]['DESCRIPTION_ERP']
                id = row[1]['ID']

                if type(grupo) == str:
                    grupo = grupo.strip()
                else:
                    grupo = ''
                
                if type(fornecedor) == str:
                    fornecedor = fornecedor.strip()
                else:
                    fornecedor = ''

                if grupo.startswith('+') or grupo.startswith('\'+'):
                    #self.cadastrar_grupo(grupo)
                    continue

                if fornecedor.startswith('+') or fornecedor.startswith('\'+'):
                    #self.cadastrar_fornecedor(fornecedor)
                    continue

                
                if type(descricao) == str:
                    descricao = descricao.strip()
                else:
                    descricao = str(descricao)
                
                if descricao == '':
                    descricao = 'Sem descrição'
                
                data_pagamento = self.obter_pagamento(row[1]['DATA'])
                data_vencimento = self.obter_vencimento(status_consumer, data_pagamento)
                
                if data_vencimento == None or grupo == '' or fornecedor == '':
                    print(f'Erro ao lancar - Grupo: {grupo} - Fo/0rnecedor: {fornecedor} - Descrição: {descricao}')
                    continue

                self.lancar(grupo, fornecedor, descricao, data_vencimento, data_pagamento, -valor)
                bd.update_pendency(id=id, status_erp='Pago')
                



    # Faz a interacao com o Consumer
    def lancar(self, grupo, fornecedor, descricao, data_vencimento, data_pagamento, valor):
        
        print(f'\nLançando no Consumer...')
        keyboard = Controller()
        
        print(f'Digitando grupo: {grupo}')
        time.sleep(3)
        keyboard.type(grupo)
        time.sleep(1)
        pyautogui.press('tab')

        print(f'Digitando fornecedor: {fornecedor}')
        time.sleep(3)
        keyboard.type(fornecedor)
        time.sleep(1)
        pyautogui.press('tab')

        print(f'Digitando descrição: {descricao}')
        time.sleep(3)
        keyboard.type(descricao)
        time.sleep(1)
        pyautogui.press('tab')

        print(f'Digitando data de vencimento: {data_vencimento}')
        time.sleep(3)
        pyautogui.typewrite(data_vencimento, interval=0.5)
        pyautogui.press('tab')

        print(f'Digitando valor {valor}')
        time.sleep(3)
        # Format to 2 decimals
        valor = '{:.2f}'.format(valor)
        valor = (str(valor)).replace('.', ',')
        pyautogui.typewrite(valor)
        pyautogui.press('tab', presses=5)
        time.sleep(1)
        pyautogui.press('space')

        print(f'Digitando data de pagamento: {data_pagamento}')
        time.sleep(3)
        pyautogui.typewrite(data_pagamento, interval=0.5)
        time.sleep(1)
        
        print('Salvando')
        time.sleep(3)
        pyautogui.press('tab', presses=5)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(3)
        



    def cadastrar_grupo(self, grupo):
        pass


    def cadastrar_fornecedor(self, fornecedor):
        pass




    def obter_vencimento(self, status_consumer, data_pagamento):

        if type(status_consumer) != str:
            return None

        if status_consumer.startswith('Venc'):
            texto = str(status_consumer.replace('Venc.:', ''))
            return texto
        if status_consumer.startswith('Novo'):
            return data_pagamento
        else:
            print('Erro ao obter vencimento, impossivel prosseguir')
            return None

    

    def obter_pagamento(self, data):

        if type(data) != str:
            data_str = data.strftime('%d/%m/%Y')
            return data_str
        return data



def main():
    consumer = Consumer()
    consumer.abrir_contas_pagar()
