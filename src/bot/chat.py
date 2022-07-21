import templateMessage, cloudFunctions, json

##############################################
#               CLOUD FUNCTION               #
##############################################

def send_message(message_type, message, chat_id):

    FUNCTION_NAME = 'function-telegram'

    # DATA
    data = {
        'message_type': message_type,
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
    pendency_id = None


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

        send_message('text', reply_message, self.chat_id)


    # Basead on status and message, return a message
    def get_reply(self, message):

        if message == '/start' or message == 'menu':
            self.status = 'menu'
            return templateMessage.msg_menu()
        
        if self.status == 'menu' and message == '1':
            return self.menu_1(message)
        
        if message == '/stop':
            return 'Bot desligado!'
        
        return 'Comand not found! Try: MENU'


    
    def get_chat_id(self):
        return self.chat_id


###################################
#             MENU 1              #
###################################

    def menu_1(self, message):

        FUNCTION_NAME = 'function-bank-next-pendency'
        DATA = {}
        next_pendency = cloudFunctions.cloud_function(FUNCTION_NAME, DATA)

        
        if next_pendency is None:
            self.status = 'menu'
            return 'Ocorreu um erro ao obter a próxima pendência, tente mais tarde...'
        
        if next_pendency == '':
            self.status = 'menu'
            return 'Não há pendências! Pode relaxar agora...'

        if self.status == 'menu' or self.status == 'menu_1_auto':
            return self.menu_1_auto(message, next_pendency)

        
            

    def menu_1_auto(self, message, next_pendency):
        
        self.status = 'menu_1_auto'
        self.pendency_id = next_pendency['ID']
        question = templateMessage.msg_make_question(next_pendency)
        send_message('text', question, self.chat_id)
        
        # Get auto classification
        FUNCTION_NAME = 'function-bank-auto-classification'
        DATA = {"description": next_pendency['DESCRICAO_ORIGINAL']}
        auto_classification = cloudFunctions.cloud_function(FUNCTION_NAME, DATA)
        
        if len(auto_classification) == 0:
            self.status = 'menu_1_manual'
            return self.menu_1_manual(message)
        
        # Get categorys
        print(auto_classification)
        send_message('inline', auto_classification, self.chat_id)
        return "Selecione uma opção..."

        


    
    def menu_1_manual(self, message):
        self.status = 'menu_1_manual'