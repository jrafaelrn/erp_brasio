import pyautogui
import webbrowser
from find_click import find_click
from time import sleep, strftime, time
from datetime import datetime
import paths
import os




def aguardar(max):

    print('\nAguarde: ', end='')
    while max > 0:
        sleep(1)
        print(f'{max}, ', end='')
        max -= 1



def entrar_sicredi():

    #Open chrome
    pyautogui.hotkey('winleft', 'r')
    pyautogui.typewrite(paths.chrome_path.replace(' %s', ''), interval=0.01)
    pyautogui.press('enter')
    aguardar(5)        
    pyautogui.hotkey('winleft', 'left')
    
    webbrowser.get(paths.chrome_path).open(paths.link_sicredi_home)
    aguardar(3)

    find_click('img/acessar_conta.png', confidence=0.8)

    #CNPJ
    find_click('img/cnpj.png', confidence=0.8, deltaY=10)
    pyautogui.typewrite(paths.cnpj, interval=0.01)
    pyautogui.press('enter')
    aguardar(5)

    # User
    pyautogui.typewrite(paths.login, interval=0.05)

    # Password
    for key in paths.senha:
        find_click(f'img/numero_{key}.png', confidence=0.85)
        pyautogui.moveTo(x=1, y=1)
        aguardar(1) 

    # Acessa
    find_click('img/acessar.png', confidence=0.7)
    aguardar(10)



def baixar_extrato(dia_base):

    #Extrato
    webbrowser.get(paths.chrome_path).open(paths.link_sicredi_extrato)
    day = dia_base.strftime('%Y-%m-%d')
    year = dia_base.strftime('%Y')
    dia = dia_base.strftime('%d/%m/%Y')

    sleep(5)
    pyautogui.press('tab', interval=0.05, presses=27)
    pyautogui.typewrite(dia, interval=0.01)
    pyautogui.press('tab')
    pyautogui.typewrite(dia, interval=0.01)

    find_click('img/pesquisar.png', confidence = 0.7)
    aguardar(3)

    pyautogui.press('end')
    aguardar(3)
    find_click('img/gerar_planilha.png', confidence = 0.7)
    aguardar(3)

    find_click('img/save_as.png', confidence = 0.7, deltaX=70, deltaY=10)
    pyautogui.typewrite(f'{paths.path_drive_sicredi_conta}', interval=0.01)
    pyautogui.press('enter')
    aguardar(3)

    sobrescreve = os.path.isfile(f'{paths.path_drive_sicredi_conta}\\{day}.xls')
    # Sobrescreve, delete file
    if sobrescreve:
        os.remove(f'{paths.path_drive_sicredi_conta}\\{day}.xls')

    pyautogui.press('tab', presses=2, interval=1)
    pyautogui.hotkey('alt', 'n')
    aguardar(1)

    name_file = ''

    # Check if dia_base is before today
    if dia_base < datetime.today():
        name_file = f'{day}-import'
    else:
        name_file = (f'{day}').replace('-import', '')
    
    pyautogui.typewrite(name_file, interval=0.01)

    aguardar(2)
    pyautogui.press('enter')

    
    #close browser
    aguardar(3)
    pyautogui.hotkey('ctrl', 'w')


def close_all():
    pyautogui.hotkey('ctrl', 'w')
    aguardar(3)
    pyautogui.hotkey('alt', 'f4')
