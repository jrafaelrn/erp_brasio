from threading import Thread
from socket import *
import bot, os, time


def listen():
    
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('0.0.0.0', 8080))
    s.listen(1)
    
    while True:
        print('\nWaiting for connection...')
        time.sleep(10)


if __name__ == '__main__':
    Thread(target=bot.start_bot).start()
    Thread(target=listen).start()