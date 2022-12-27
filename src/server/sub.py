import os, datetime, from_bank_to_bd, time, say
from google import pubsub_v1



downloads_day = []



def callback_import(message):

    global downloads_day
    message = message.message
    message_text = str(message.data)
    day_str = None
    
    print(f'Receiving message: {message_text} - Date: {message.publish_time}')

    publish_time_brasilia = message.publish_time.replace(tzinfo=datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
    
    if message_text.find('yesterday') != -1:
        yesterday = publish_time_brasilia - datetime.timedelta(days=1)
        day_str = yesterday.strftime('%d/%m/%Y')

    elif message_text.find('today') != -1:
        day_str = publish_time_brasilia.strftime('%d/%m/%Y')    

    downloads_day.append(day_str)

      

def listen_download():

    global downloads_day
    subscriber = pubsub_v1.SubscriberClient()

    PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
    SUBSCRIPTION = 'download-all-banks-sub'
    
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION)
    
    
    while True:
        
        try:

            # Open the subscription, passing the callback.
            print(f'Listening for messages on {SUBSCRIPTION} - Now: {time.strftime("%H:%M:%S")}')

            response = subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": 50,
                }
            )

            print(f'Received {len(response.received_messages)} messages.')
            
            if len(response.received_messages) == 0:
                time.sleep(10)
                continue
                            
            
            for msg in response.received_messages:
                callback_import(msg)

            # Remove duplicates
            downloads_day = list(set(downloads_day))

            #say.now('Starting download from banks, in 3, 2, 1, lets go!')
            from_bank_to_bd.download_all(downloads_day, import_bd=True)
            downloads_day = []
            
            ack_ids = [msg.ack_id for msg in response.received_messages]
            print(f'IMPORT - Total of ACK messages: {len(ack_ids)}')

            if len(ack_ids) > 0:

                request = {
                    "subscription" :subscription_path,
                    "ack_ids" : ack_ids
                }
                
                response = subscriber.acknowledge(request)
                print(f'\tIMPORT - Acknowledged messages response: {response}')

                request = pubsub_v1.AcknowledgeRequest(
                    subscription=subscription_path,
                    ack_ids=ack_ids
                )

                response = subscriber.acknowledge(request)
                print(f'\tIMPORT - Acknowledged messages response: {response}')
                    

                
            time.sleep(10)

        except Exception as e:
            print(f'\n!!!IMPORT Error: {e}')
            time.sleep(10)
            continue

    subscriber.close()