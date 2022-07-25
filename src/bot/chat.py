from unicodedata import category
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


def update_pendency(id, category_erp, entity_erp, description_erp):

    FUNCTION_NAME = 'function-bd-transaction'

    # DATA
    data = {
        'id': id,
        'category_erp': category_erp,
        'entity_erp': entity_erp,
        'description_erp': description_erp,
        'status_erp' : 'Pago'
    }

    # ARGS
    args = 'type=update'

    # CLOUD FUNCTION
    cloudFunctions.cloud_function(FUNCTION_NAME, data, args)


##############################################
#                    CHAT                    #
##############################################

class chat(object):

    username = None
    chat_id = None
    status = None
    pendency_id = None
    category_actual = None
    entity_actual = None
    description_actual = None


    def __init__(self, username, chat_id):
        self.username = username
        self.chat_id = chat_id
        self.status = 'any'


    ###################################
    #         REPLY MESSAGE           #
    ###################################

    def reply(self, message):

        reply_message = self.get_reply(message)
        send_message('text', reply_message, self.chat_id)


    # Basead on status and message, return a message
    def get_reply(self, message):

        if message == '/start' or message.lower() == 'menu':
            self.status = 'menu'
            return templateMessage.msg_menu()
        
        if (self.status == 'menu' and message == '1') or self.status.startswith('menu_1') or message == '/pendencias':
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

        has_finished, next_pendency = self.get_next_pendency()
        
        if has_finished:
            self.status = 'menu'
            return 'Não há pendências! Pode relaxar...'

        if self.status == 'menu' or self.status.startswith('menu_1_auto'):
            return self.menu_1_auto(message, next_pendency)

    

    def get_next_pendency(self):
            
        FUNCTION_NAME = 'function-bank-next-pendency'
        DATA = {}
        next_pendency = cloudFunctions.cloud_function(FUNCTION_NAME, DATA)
        
        try:
            if next_pendency['error'] == 'No pendency found':
                return True, None
        except:
            pass
        
        return False, next_pendency

    
    ###################################
    #         MENU 1  - AUTO          #
    ###################################

    def menu_1_auto(self, message, next_pendency):
        
        if self.status == 'menu':
            
            # Make a question
            question = templateMessage.msg_make_question(next_pendency)
            send_message('text', question, self.chat_id)
            
            # Get auto classification
            FUNCTION_NAME = 'function-bank-auto-classification'
            DATA = {"description": next_pendency['DESCRICAO_ORIGINAL']}
            auto_classification = cloudFunctions.cloud_function(FUNCTION_NAME, DATA)

            if len(auto_classification) == 0:
                self.status = 'menu_1_manual'
                return self.menu_1_manual(message)
            
            # Get ERP pendency
            entities = []

            for classification in auto_classification:
                entities.append(classification['entity'])

            #Remove duplicates and get the pendencies
            entities = list(set(entities))
            FUNCTION_NAME = 'function-erp-pendency'
            DATA = {"entities": entities}
            erp_pendencies = cloudFunctions.cloud_function(FUNCTION_NAME, DATA)

            # Create options to send INLINE
            options_list = []

            # Try append ERP Pendencys
            try:
                
                if erp_pendencies['error'] == 'No pendency found':
                    pass
            
            except:
                
                options = erp_pendencies['pendencies']
                for option in options:
                    
                    pendencies = option['pendency']

                    for pendency in pendencies:

                        category = pendency['category']
                        entity = pendency['entity']
                        description = pendency['description']
                        due_date = pendency['due_date']
                        value = float(pendency['value'])
                        value = f'{value:.2f}'
                        value = value.replace('.', ',') 
                        
                        opt_list = f'{category} - {entity} - {description} - Venc.: {due_date} - R$ {value}'
                        options_list.append(pendency)

            # Try append auto classification
            for classification in auto_classification:
                category = classification['category']
                entity = classification['entity']
                keyboard_button = f'{category} - {entity}'
                options_list.append(keyboard_button)

            # Append new classification
            options_list.append('Nova classificação')   
            
            # Send
            print(options_list)
            send_message('inline', options_list, self.chat_id)
            self.status = 'menu_1_auto_classification'
            return ""


        if self.status == 'menu_1_auto_classification':

            if message.startswith('->'):
                self.status = 'menu_1_manual'
                return self.menu_1_manual(message)

            self.category_actual = message.split(' - ')[0]
            self.entity_actual = message.split(' - ')[1]

            # Get description
            self.status = 'menu_1_auto_classification_description'
            return 'Qual a descrição da pendência?'

        
        if self.status == 'menu_1_auto_classification_description':

            self.pendency_id = next_pendency['ID']
            self.description_actual = message
            self.status = 'menu'
            update_pendency(self.pendency_id, self.category_actual, self.entity_actual, self.description_actual)

            msg_success = templateMessage.msg_success(self.category_actual, self.entity_actual, self.description_actual)
            send_message('text', msg_success, self.chat_id)


            #Check if there is another pendency
            has_finished, next_pendency = self.get_next_pendency()
            
            if has_finished:
                return 'Uhuuul, acabooou!! Agora pode ir gastar mais...'

            return self.menu_1_auto('1', next_pendency)


        

    ###################################
    #         MENU 1  - MANUAL        #
    ###################################
    
    def menu_1_manual(self, message):

        if self.status == 'menu_1_manual':
            pass