import os, datetime, from_bank_to_bd, time, say
from google import pubsub_v1



downloads_day = []
working = False



def callback_import(message):

    global downloads_day
    message = message.message
    
    print(f'Receiving message: {message.data} - Date: {message.publish_time}')

    publish_time_brasilia = message.publish_time.replace(tzinfo=datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
    yesterday = publish_time_brasilia - datetime.timedelta(days=1)
    yesterday_str = yesterday.strftime('%d/%m/%Y')

    downloads_day.append(yesterday_str)

      

def listen_import():

    global working
    global downloads_day

    while True:
        
        try:
            with pubsub_v1.SubscriberClient() as subscriber:

                PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
                SUBSCRIPTION = 'import_bd_from_banks-topic-sub'
                
                subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION)

                # Open the subscription, passing the callback.
                print(f'Listening for messages on {SUBSCRIPTION} - Now: {time.strftime("%H:%M:%S")}')

                response = subscriber.pull(
                    request={
                        "subscription": subscription_path,
                        "max_messages": 50,
                    }
                )
                
                if len(response.received_messages) == 0:
                    continue
                
                if working:
                    seconds  = 10
                    print(f'\n!!! Sales day still Working... Try again in {seconds} seconds !!!\n')
                    time.sleep(seconds)
                    continue
                

                working = True     
                for msg in response.received_messages:
                    callback_import(msg)

                request_more_time = pubsub_v1.ModifyAckDeadlineRequest(
                    subscription=subscription_path,
                    ack_ids=[msg.ack_id for msg in response.received_messages],
                    ack_deadline_seconds=600
                )
                subscriber.modify_ack_deadline(request_more_time)
                
                
                print('Blocking threads...')
                say.now('Starting download from banks, in 3, 2, 1, lets go!')
                #from_bank_to_bd.download_all(downloads_day, import_bd=True)
                downloads_day = []
                
                ack_ids = [msg.ack_id for msg in response.received_messages]
                print(f'IMPORT - Total of ACK messages: {len(ack_ids)}')

                if len(ack_ids) > 0:

                    request = pubsub_v1.AcknowledgeRequest(
                        subscription =  subscription_path,
                        ack_ids = ack_ids,
                    )
                    
                    response = subscriber.acknowledge(request)
                    print(f'IMPORT - Acknowledged messages: {response}')

                    
                print('Unblocking threads...')
                print('Finished !!')        
                working = False
                time.sleep(10)

        except Exception as e:
            print(f'\n!!!IMPORT Error: {e}')
            time.sleep(10)
            continue


def listen_sales_day():

    global working
    time.sleep(3)


    while True:

        try:
            
            with pubsub_v1.SubscriberClient() as subscriber:

                PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
                SUBSCRIPTION = 'sub-check-sales-day'
                
                subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION)

                # Open the subscription, passing the callback.
                print(f'Listening for messages on {SUBSCRIPTION} - Now: {time.strftime("%H:%M:%S")}')

                response = subscriber.pull(
                    request={
                        "subscription": subscription_path,
                        "max_messages": 50,
                    }
                )
                
                if len(response.received_messages) == 0:
                    continue
                
                if working:
                    seconds  = 10
                    print(f'\n!!! Import Bank still working... Try again in {seconds} seconds !!!\n')
                    time.sleep(seconds)
                    continue
                
                
                
                request_more_time = pubsub_v1.ModifyAckDeadlineRequest(
                    subscription=subscription_path,
                    ack_ids=[msg.ack_id for msg in response.received_messages],
                    ack_deadline_seconds=600
                )
                subscriber.modify_ack_deadline(request_more_time)
                
                working = True
                print('SALES-DAY Blocking threads...')          
                say.now('Starting to check sales day, in 3, 2, 1, lets go!')
                today = datetime.datetime.now().strftime('%d/%m/%Y')     
                #from_bank_to_bd.download_all([today], import_bd=False)
                downloads_day = []

                ack_ids = [msg.ack_id for msg in response.received_messages]
                print(f'SALES-DAY - Total of ACK messages: {len(ack_ids)}')

                if len(ack_ids) > 0:
                    
                    request = pubsub_v1.AcknowledgeRequest(
                        subscription =  subscription_path,
                        ack_ids = ack_ids,
                    )
                    
                    response = subscriber.acknowledge(request)
                    print(f'SALES-DAY - Acknowledged messages: {response}')
                
                print('Unblocking threads...')
                print('Finished !!')
                working = False               
                time.sleep(10)

        except Exception as e:
            print(f'\n!!!SALES-DAY Error: {e}')
            time.sleep(10)
            continue