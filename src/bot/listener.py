import time
import socket

HOST = '127.0.0.1'
PORT = 47221


def start_listener():

    print('Starting listener...')

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
                print(data.decode('utf-8'))
                time.sleep(3)
                conn.sendall(data)

            print('Connection closed.')

    