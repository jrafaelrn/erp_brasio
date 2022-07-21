from threading import Thread
import bot

if __name__ == '__main__':
    Thread(target=bot.start_bot).start()    
    print('Bot finished!')