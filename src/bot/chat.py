import templateMessage, cloudFunctions

##############################################
#               CLOUD FUNCTION               #
##############################################

def send_message(message, chat_id):

    FUNCTION_NAME = 'function-telegram'

    # DATA
    data = {
        'message_type': 'text',
        'content' : message,
        'chat_id': chat_id
    }

    # CLOUD FUNCTION
    cloudFunctions.cloud_function(FUNCTION_NAME, data)




##############################################
#                    CHAT                    #
##############################################

class chat(object):

    username = None
    chat_id = None
    status = None


    def __init__(self, username, chat_id):
        self.username = username
        self.chat_id = chat_id
        self.status = 'any'


###################################
#         REPLY MESSAGE           #
###################################

    def reply(self, message):

        message = message.lower()
        reply_message = self.get_reply(message)

        send_message(reply_message, self.chat_id)


    def get_reply(self, message):

        if message == '/start' or message == 'menu':
            return templateMessage.msg_menu()
        elif message == '/help':
            return 'Comandos disponíveis: /start'
        elif message == '/stop':
            return 'Bot desligado!'
        else:
            return 'Comand not found! Try: MENU'


    
    def get_chat_id(self):
        return self.chat_id