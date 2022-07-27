import to_erp, threading, sub



consumer_pendencys = []

# Faz a interacao com o Consumer
def main():

    global consumer_pendencys
    
    if len(consumer_pendencys) > 0:
        to_erp.main()



# PUB/SUB
def subscribe_imports():
    sub.listen_import()

def subscribe_sales_day():
    sub.listen_sales_day()




#####################
#     THREADS      #
#####################

thread_consumer = threading.Thread(target=main)
thread_consumer.start()

thread_subscribe = threading.Thread(target=subscribe_imports)
thread_subscribe.start()

thread_sales_day = threading.Thread(target=subscribe_sales_day)
thread_sales_day.start()