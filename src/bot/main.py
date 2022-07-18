from threading import Thread
import bot
import listener


if __name__ == '__main__':
    Thread(target=bot.start_bot).start()
    Thread(target=listener.start_listener).start()
