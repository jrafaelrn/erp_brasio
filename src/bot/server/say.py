import os, time, pyautogui
from gtts import gTTS

def now(text):

    tts = gTTS(text, lang='en')
    tts.save('tts.mp3')
    os.system('tts.mp3')
    time.sleep(7)
    pyautogui.hotkey('alt', 'f4')