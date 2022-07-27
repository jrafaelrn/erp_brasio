import pyautogui, time, os, pathlib


def find_click(imagem, deltaX=0, deltaY=0, confidence=0.9, clicks=1):
    
    print(f'\nLocalizando {imagem} DeltaX= {deltaX} DeltaY= {deltaY} Confidence= {confidence}')
    local = None

    #Get absolute path
    path_absolute = pathlib.Path().resolve()
    path_absolute = (f'{path_absolute}/src/bot/server/').replace('\\', '/')
    imagem = (f'{path_absolute}{imagem}')
    imagem_errror = (f'{path_absolute}img/erro.png')

    while True:
        
        tentativas = 1

        while tentativas <= 5 and local is None:
            print(f'\tTentativa {tentativas}')
            local = pyautogui.locateCenterOnScreen(imagem, confidence=confidence)
            tentativas += 1
            time.sleep(2)

        if local is None:

            has_erro = None
            has_erro = pyautogui.locateCenterOnScreen(imagem_errror, confidence=0.5)

            if not(has_erro is None):
                print('\n\tRefresh page...\n')
                pyautogui.press('f5')
                time.sleep(15)
            else:
                confidence -= 0.05
                print(f'\tReduzindo Confidence from {confidence+0.05} to {confidence}')

        else:

            break


    print(f'\t\tLocalizado em {local}')
    print(f'\t\tClicando em {local.x+deltaX}, {local.y+deltaY}')
    pyautogui.click(x=local.x + deltaX, y=local.y + deltaY, clicks=clicks, interval=1)
