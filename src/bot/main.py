from threading import Thread
import bot, os, time, socket


def listen():

    HOST = '0.0.0.0'
    PORT = 8080
    
    while True:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:

            soc.bind((HOST, PORT))
            soc.listen()
            conn, addr = soc.accept()

            with conn:

                print(f'Connected by {addr}')

                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    data_decoded = data.decode('utf-8')
                    print(data_decoded)
                    time.sleep(1)
                    conn.sendall(200)

                print('Connection closed.')
        
        time.sleep(10)
        print('Keep alive...')


if __name__ == '__main__':
    Thread(target=bot.start_bot).start()
    Thread(target=listen).start()
    
    print('Bot finished!')