from flask import Flask,session
from flask_session import Session
import requests 
from flask import request
from flask import jsonify
from response_util import get_failed_response,get_success_response 
import sys
from flask_caching import Cache
import socket
import logging
import threading
import multiprocessing
from threading import Thread
import time

# logging.basicConfig(filename=str(sys.argv[3])+".log", level=logging.DEBUG, format='%(asctime)s %(message)s %(threadName)s', filemode='w')

config = {          
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 0
}

app = Flask(__name__)

###### Setting up logs for frontend and heatbeat ######
formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# main file logger
app.logger = setup_logger('main', str(sys.argv[3])+".log")
app.logger.info('This is a main message')

# heartbeat file logger
hb_logger = setup_logger('hb_logger', 'heartbeat.log')
hb_logger.info('This is an heartbeat message')

##########################################################
 
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

###### Setting up the config variables ######
app.config.from_mapping(config)
cache = Cache(app)
app.config['load_balancer_catalog'] = 0
app.config['load_balancer_order'] = 0
app.config['catalogA_status'] = "DOWN"
app.config['catalogB_status'] = "DOWN"
app.config['orderA_status'] = "DOWN"
app.config['orderB_status'] = "DOWN"
#############################################

###### Setting up the locks ######
order_lock = threading.Lock()
catalog_lock = threading.Lock()
hb_lock = threading.Lock()
##################################

###### Setting up global variables ######
CATALOG_SERVER_A = {"type": "catalog", "url": str(sys.argv[4])}
CATALOG_SERVER_B = {"type": "catalog", "url": str(sys.argv[5])}
ORDER_SERVER_A = {"type": "order", "url": str(sys.argv[6])}
ORDER_SERVER_B = {"type": "order", "url": str(sys.argv[7])}
##################################

# class hbCatalogA(Thread):
#     def __init__(self, ip, port):
#         Thread.__init__(self)
#         self.running = True
#         self.ip = ip
#         self.port = port

#     def run(self):
#         while self.running:
#             if isUp(self.ip, self.port):
#                 app.config['catalogA_status'] = "UP"
#             else:
#                 app.config['catalogA_status'] = "DOWN"
#             time.sleep(1)
#     def stop(self):
#         self.running = False


def isUp(ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

def heartbeat(url, server_status):
    while(True):
        ip = url.split(':')[1].split('/')[-1]
        port = url.split(':')[2]

        if isUp(ip, port):
            app.config[server_status] = "UP"
        else:
            app.config[server_status] = "DOWN"
        hb_logger.info("The %s : %s"%(server_status, app.config[server_status]))
        time.sleep(1)

def cache_key():
    return request.args

def start_heartbeats():
    catalogA_heartbeat_thread = Thread(target=heartbeat, args=(CATALOG_SERVER_A['url'], 'catalogA_status',))
    catalogB_heartbeat_thread = Thread(target=heartbeat, args=(CATALOG_SERVER_B['url'], 'catalogB_status',))
    orderA_heartbeat_thread = Thread(target=heartbeat, args=(ORDER_SERVER_A['url'], 'orderA_status',))
    orderB_heartbeat_thread = Thread(target=heartbeat, args=(ORDER_SERVER_B['url'], 'orderB_status',))
    catalogA_heartbeat_thread.start()
    catalogB_heartbeat_thread.start()
    orderA_heartbeat_thread.start()
    orderB_heartbeat_thread.start()
    # CatalogA_heartbeat = hbCatalogA(CATALOG_SERVER_A['url'].split(':')[0]+CATALOG_SERVER_A['url'].split(':')[1],CATALOG_SERVER_A['url'].split(':')[2])
    # CatalogB_heartbeat = hbCatalogB(CATALOG_SERVER_B['url'].split(':')[0]+CATALOG_SERVER_B['url'].split(':')[1],CATALOG_SERVER_B['url'].split(':')[2])
    # OrderA_heartbeat = hbOrderA(ORDER_SERVER_A['url'].split(':')[0]+ORDER_SERVER_A['url'].split(':')[1],ORDER_SERVER_A['url'].split(':')[2])
    # OrderB_heartbeat = hbOrderB(ORDER_SERVER_B['url'].split(':')[0]+ORDER_SERVER_B['url'].split(':')[1],ORDER_SERVER_B['url'].split(':')[2])

    # CatalogA_heartbeat.start()
    # CatalogB_heartbeat.start()
    # OrderA_heartbeat.start()
    # OrderB_heartbeat.start()

# defining the default page
@app.route('/', methods=['GET'])
def hello_world():
    app.logger.info("I am here")
    return "Welcome to Book Store!"

# the buy method which makes calls to the order server to buy an item based on provided item id
@app.route('/buy', methods=['GET'])
def buy():
    try:
        data = request.args
        id=data["id"]
        app.logger.info("Buy method called with the item with id '%s' in catalog server." % (id))
        order_lock.acquire()
        if app.config['load_balancer_order'] != None and app.config['load_balancer_order'] == 0:
            app.config['load_balancer_order'] = 1
            order_lock.release()
            results=requests.get("%s/buy/%s"%(ORDER_SERVER_A["url"],id))
            results=results.json()
        else:
            app.config['load_balancer_order'] = 0
            order_lock.release()
            results=requests.get("%s/buy/%s"%(ORDER_SERVER_B["url"],id))
            results=results.json()
        cache.clear()
        app.logger.info("Purchase of item '%s' successfull."%(id))
        return results
    except Exception as e:
        app.logger.info("Failed to connect to order server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))


#the search method makes calls to the catalog server and searches for items based on topic name 
@app.route('/search',methods=['GET'])
@cache.cached(key_prefix = cache_key)
def search():
    try:
        if 'topic' in request.args:
            topic=request.args['topic']
        else:
            return "Error: No topic field provided. Please specify a topic."
        app.logger.info("Search method called with the topic name '%s' in catalog server." % (topic))
        catalog_lock.acquire()
        if app.config['load_balancer_catalog'] != None and app.config['load_balancer_catalog'] == 0:
            app.config['load_balancer_catalog'] = 1
            catalog_lock.release()
            results=requests.get("%s/item?topic=%s"%(CATALOG_SERVER_A["url"],topic))
            app.logger.info("Searching of items with topic '%s' successful."%(topic))
        else:
            app.config['load_balancer_catalog'] = 0
            catalog_lock.release()
            results=requests.get("%s/item?topic=%s"%(CATALOG_SERVER_B["url"],topic))
            app.logger.info("Searching of items with topic '%s' successful."%(topic))
        results=results.json()
        return results
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))


# the lookup method makes calls to the catalog server and searches for the item corresponding to item id
@app.route('/lookup',methods=['GET'])
@cache.cached(key_prefix = cache_key)
def lookup():
    try:
        if 'id' in request.args:
            id=request.args['id']
        else:
            return "Error: No id field provided. Please specify an id."
        app.logger.info("Lookup method called with the id '%s' in catalog server." % (id))
        catalog_lock.acquire()
        if app.config['load_balancer_catalog'] != None and app.config['load_balancer_catalog'] == 0:
            app.config['load_balancer_catalog'] = 1
            catalog_lock.release()
            results=requests.get("%s/item/%s"%(CATALOG_SERVER_A["url"],id))
            results=results.json()
        else:
            app.config['load_balancer_catalog'] = 0
            catalog_lock.release()
            results=requests.get("%s/item/%s"%(CATALOG_SERVER_B["url"],id))
            results=results.json()
        app.logger.info("Looking Up of item with id '%s' successful."%(id))
        return results
        
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))

if __name__=='__main__':
    start_heartbeats()
    app.run(host=str(sys.argv[1]), port=str(sys.argv[2]))
