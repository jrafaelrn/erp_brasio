from unicodedata import category
import templateMessage, cloudFunctions, json, random

phrases = [
    'Oooh Glooooria, terminou, agora pode ir gastar mais...',
    'Vivaaaa, acabamos!! Agora vai lavar uma louça... ',
    'É isso aí, não tem mais jeito, acabou....boa sorte!!',
    'Graças a Deeeeeus isso acabou!! Agora vai vender, mulher...'
]

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


def update_pendency(id, category_erp, entity_erp, description_erp, status_erp):

    FUNCTION_NAME = 'function-bd-transaction'

    # DATA
    data = {
        'id': id,
        'category_erp': category_erp,
        'entity_erp': entity_erp,
        'description_erp': description_erp,
        'status_erp' : status_erp
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

        if self.status.startswith('menu_1_manual'):
            return self.menu_1_manual(message, next_pendency)

    

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

    # Create options to send INLINE
    options_list = []
    
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
                return self.menu_1_manual(message, next_pendency)
            
            # Get ERP pendency
            entities = []

            for classification in auto_classification:
                entities.append(classification['entity'])

            #Remove duplicates and get the pendencies
            entities = list(set(entities))
            FUNCTION_NAME = 'function-erp-pendency'
            DATA = {"entities": entities}
            erp_pendencies = cloudFunctions.cloud_function(FUNCTION_NAME, DATA)

            options_list = []
            
            # Try append ERP Pendencys
            try:
                
                if erp_pendencies['error'] == 'No pendency found':
                    pass
            
            except:
                
                options = erp_pendencies['pendencies']
                for option in options:
                    
                    pendencies = option['pendencies']

                    for pendency in pendencies:

                        category = pendency['category']
                        entity = pendency['entity']
                        description = pendency['description']
                        due_date = pendency['due_date']
                        value = float(pendency['value'])
                        value = f'{value:.2f}'
                        value = value.replace('.', ',') 
                        
                        opt_list = f'{category} - {entity} - {description} - Venc.: {due_date} - R$ {value}'
                        self.options_list.append(opt_list)

            # Try append auto classification
            for classification in auto_classification:
                category = classification['category']
                entity = classification['entity']
                keyboard_button = f'{category} - {entity}'
                self.options_list.append(keyboard_button)

            # Append new classification
            self.options_list.append('Nova classificação')   
            
            # Send
            #print(options_list)
            send_message('inline', self.options_list, self.chat_id)
            self.status = 'menu_1_auto_classification'
            return ""


        if self.status == 'menu_1_auto_classification':

            if self.options_list[int(message)] == 'Nova classificação':
                self.status = 'menu_1_manual'
                return self.menu_1_manual(message, next_pendency)

            self.category_actual = self.options_list[int(message)].split(' - ')[0]
            self.entity_actual = self.options_list[int(message)].split(' - ')[1]

            try:
                self.description_actual = self.options_list[int(message)].split(' - ')[2]
                status_erp = self.options_list[int(message)].split(' - ')[3]
                self.status = 'menu'
                update_pendency(next_pendency['ID'], self.category_actual, self.entity_actual, self.description_actual, status_erp)

                msg_success = templateMessage.msg_success(self.category_actual, self.entity_actual, self.description_actual)
                send_message('text', msg_success, self.chat_id)

                has_finished, next_pendency = self.get_next_pendency()

                if has_finished:
                    return random.choice(phrases)
            
            except:
                pass

            # Get description
            self.status = 'menu_1_auto_classification_description'
            return 'Qual a descrição da pendência?'

        
        if self.status == 'menu_1_auto_classification_description':

            self.pendency_id = next_pendency['ID']
            self.description_actual = message
            self.status = 'menu'
            update_pendency(self.pendency_id, self.category_actual, self.entity_actual, self.description_actual, 'Novo')

            msg_success = templateMessage.msg_success(self.category_actual, self.entity_actual, self.description_actual)
            send_message('text', msg_success, self.chat_id)


            #Check if there is another pendency
            has_finished, next_pendency = self.get_next_pendency()
            
            if has_finished:
                return random.choice(phrases)

            return self.menu_1_auto('1', next_pendency)


        

    ###################################
    #         MENU 1  - MANUAL        #
    ###################################
    
    def menu_1_manual(self, message, next_pendency):

        
        if self.status == 'menu_1_manual':
            
            self.categories = templateMessage.msg_categories_erp()
            self.status = 'menu_1_manual_category'
            send_message('inline', self.categories, self.chat_id)
            return 'Clique em uma categoria'

        
        if self.status == 'menu_1_manual_category':

            self.category_actual = self.categories[int(message)]
            self.suppliers = templateMessage.msg_suppliers_erp()
            self.status = 'menu_1_manual_supplier'
            send_message('inline', self.suppliers, self.chat_id)
            return 'Clique em um fornecedor'


        if self.status == 'menu_1_manual_supplier' or self.status == 'menu_1_manual_supplier_new':

            try:
                self.entity_actual = self.suppliers[int(message)]
            except:
                self.entity_actual = message

            if self.entity_actual == 'Novo fornecedor':
                self.status = 'menu_1_manual_supplier_new'
                return 'Qual o nome do novo fornecedor?'

            if self.status == 'menu_1_manual_supplier_new':
                new_supplier = f'+{message}'
                self.entity_actual = new_supplier

            self.status = 'menu_1_manual_description'
            msg = 'Qual a descrição?'
            return msg

        
        if self.status == 'menu_1_manual_description':

            self.description_actual = message
            self.status = 'menu'
            pendency_id = next_pendency['ID']
            update_pendency(pendency_id, self.category_actual, self.entity_actual, self.description_actual, 'Novo')

            msg_success = templateMessage.msg_success(self.category_actual, self.entity_actual, self.description_actual)
            send_message('text', msg_success, self.chat_id)


            #Check if there is another pendency
            has_finished, next_pendency = self.get_next_pendency()
            
            if has_finished:
                return random.choice(phrases)

            return self.menu_1_auto('1', next_pendency)