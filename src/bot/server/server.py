import to_erp, threading, sub



consumer_pendencys = []

# Faz a interacao com o Consumer
def main():

    global consumer_pendencys
    
    if len(consumer_pendencys) > 0:
        to_erp.main()



# PUB/SUB
def subscribe_download_from_banks():
    sub.listen_download()





#####################
#     THREADS      #
#####################

thread_consumer = threading.Thread(target=main)
thread_consumer.start()

thread_subscribe = threading.Thread(target=subscribe_download_from_banks)
thread_subscribe.start()
