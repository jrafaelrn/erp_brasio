from ast import ImportFrom
import time, socket, telegram


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
                data_decoded = data.decode('utf-8')
                print(data_decoded)
                time.sleep(1)

                if handle_message(data_decoded):
                    conn.sendall('OK')
                else:
                    conn.sendall('ERROR')

            print('Connection closed.')




def handle_message(data):

    print(f'Handling message: {data}')

    msg_type = data['message_type']
    content = data['content']
    chat_id = data['chat_id']


    if msg_type == 'text':
        return send_message(content, chat_id)




def send_message(content, chat_id):

    try:
        telegram_bot = telegram()
        telegram_bot.sendMessage(content, chat_id)
        return True
    except Exception as e:
        print(f'Error sending message: {e}')
        return False

