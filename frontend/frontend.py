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

config = {          
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 0
}

app = Flask(__name__)

###### Setting up logs for frontend and heatbeat ######
formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.DEBUG):
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

#Function to check if the specified <IP,port> is up
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

# defining the default page
@app.route('/', methods=['GET'])
def hello_world():
    app.logger.info("I am here")
    return "Welcome to Book Store!"

##################################
# We have implemented round robin load-balancing in our system which is handled via 2
# load balancing catalog variables i.e load_balancer_catalog and load_balancer_order.
# Their value keeps flipping between 0 and 1 after every use.
# We have also implemented the heartbeat mechanism which we use to determine whether
# the servers which we are about to contact are up and running.
# We have also implemented locking to prevent concurrent access to the load-balancer
# variables which ensures smooth load balancing in case of parallel threads.
# We also have our fault tolerance mechanism which contacts the other catalog/order
# server in case heartbeat of the initial server is down or there was any issue connecting
# to the first server.
##################################

# the buy method which makes calls to the order server to buy an item based on provided item id
@app.route('/buy', methods=['GET'])
def buy():
    try:
        data = request.args
        id=data["id"]
        app.logger.info("Buy method called with the item with id '%s' in order server." % (id))
        order_lock.acquire()
        if app.config['load_balancer_order'] == 0:
            if app.config['orderA_status'] == "UP" and app.config['catalogA_status'] == "UP":
                app.config['load_balancer_order'] = 1
                order_lock.release()
                app.logger.debug('Order A is up, Calling Order Server A')
                results=requests.get("%s/buy/%s"%(ORDER_SERVER_A["url"],id))
            else:
                if app.config['orderB_status'] == "UP" and app.config['catalogB_status'] == "UP":
                    app.config['load_balancer_order'] = 1
                    order_lock.release()
                    app.logger.debug('Order A is down, Calling Order Server B')
                    results=requests.get("%s/buy/%s"%(ORDER_SERVER_B["url"],id))
                else:
                    raise Exception("Both order servers are down")

        else:
            if app.config['orderB_status'] == "UP" and app.config['catalogB_status'] == "UP":
                app.config['load_balancer_order'] = 0
                order_lock.release()
                app.logger.debug('Order B is up, Calling Order Server B')
                results=requests.get("%s/buy/%s"%(ORDER_SERVER_B["url"],id))
            else:
                if app.config['orderA_status'] == "UP" and app.config['catalogA_status'] == "UP":
                    app.config['load_balancer_order'] = 0
                    order_lock.release()
                    app.logger.debug('Order B is down, Calling Order Server A')
                    results=requests.get("%s/buy/%s"%(ORDER_SERVER_A["url"],id))
                else:
                    raise Exception("Both order servers are down")
        
        app.logger.info("Purchase of item '%s' successfull."%(id))
        if results.status_code != 200:
            error_message = results.json()['message']
            return get_failed_response(message = str(error_message))
        else:
            cache.clear()
            return get_success_response("frontend", output=[], message = str(results.json()['message']))

    except requests.exceptions.ConnectionError as e:
        app.logger.info("Connection error, sending request to the other order server")
        try:
            if app.config['load_balancer_order'] == 1:
                app.logger.debug('Order A has crashed, Calling Order Server B')
                results = requests.get("%s/item?topic=%s"%(ORDER_SERVER_B["url"],id))
            else:
                app.logger.debug('Order B has crashed, Calling Order Server A')
                results = requests.get("%s/item?topic=%s"%(ORDER_SERVER_A["url"],id))
            if results.status_code != 200:
                error_message = results.json()['message']
                return get_failed_response(message = str(error_message))
            else:
                cache.clear()
                return get_success_response("frontend", output=[], message = str(results.json()['message']))
        except:

            app.logger.info("Failed to connect to the other catalog server. Error: %s" % (str(e)))
            return get_failed_response(message=str(e))
    except Exception as e:
        app.logger.info("Failed to buy the item. Error: %s" % (str(e)))
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
        if app.config['load_balancer_catalog'] == 0:
            if app.config['catalogA_status'] == "UP":
                app.config['load_balancer_catalog'] = 1
                catalog_lock.release()
                app.logger.debug('Catalog A is up, Calling Catalog Server A')
                results=requests.get("%s/item?topic=%s"%(CATALOG_SERVER_A["url"],topic))
                app.logger.info("Searching of items with topic '%s' successful."%(topic))
            else:
                if app.config['catalogB_status'] == "UP":
                    app.config['load_balancer_catalog'] = 1
                    catalog_lock.release()
                    app.logger.debug('Catalog A is down, Calling Catalog Server B')
                    results=requests.get("%s/item?topic=%s"%(CATALOG_SERVER_B["url"],topic))
                    app.logger.info("Searching of items with topic '%s' successful."%(topic))
                else:
                    raise Exception("Both catalog servers are down")    
        else:
            if app.config['catalogB_status'] == "UP":
                app.config['load_balancer_catalog'] = 0
                catalog_lock.release()
                app.logger.debug('Catalog B is up, Calling Catalog Server B')
                results=requests.get("%s/item?topic=%s"%(CATALOG_SERVER_B["url"],topic))
                app.logger.info("Searching of items with topic '%s' successful."%(topic))
            else:
                if app.config['catalogA_status'] == "UP":
                    app.config['load_balancer_catalog'] = 0
                    catalog_lock.release()
                    app.logger.debug('Catalog B is down, Calling Catalog Server A')
                    results=requests.get("%s/item?topic=%s"%(CATALOG_SERVER_A["url"],topic))
                    app.logger.info("Searching of items with topic '%s' successful."%(topic))
                else:
                    raise Exception("Both catalog servers are down")
        results=results.json()
        return results
    except requests.exceptions.ConnectionError as e:
        app.logger.info("Connection error, sending request to the other catalog server")
        try:
            if app.config['load_balancer_catalog'] == 1:
                app.logger.debug('Catalog A has crashed, Calling Catalog Server B')
                results = requests.get("%s/item?topic=%s"%(CATALOG_SERVER_B["url"],topic))
            else:
                app.logger.debug('Catalog B has crashed, Calling Catalog Server A') 
                results = requests.get("%s/item?topic=%s"%(CATALOG_SERVER_A["url"],topic))
            results = results.json()
            return results
        except:
            app.logger.info("Failed to connect to the other catalog server. Error: %s" % (str(e)))
            return get_failed_response(message=str(e))
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
        if app.config['load_balancer_catalog'] == 0:
            if app.config['catalogA_status'] == "UP":
                app.config['load_balancer_catalog'] = 1
                catalog_lock.release()
                app.logger.debug('Catalog A is up, Calling Catalog Server A')
                results=requests.get("%s/item/%s"%(CATALOG_SERVER_A["url"],id))
                app.logger.info("Searching of items with id '%s' successful."%(id))
            else:
                if app.config['catalogB_status'] == "UP":
                    app.config['load_balancer_catalog'] = 1
                    catalog_lock.release()
                    app.logger.debug('Catalog A is down, Calling Catalog Server B')
                    results=requests.get("%s/item/%s"%(CATALOG_SERVER_B["url"],id))
                    app.logger.info("Searching of items with id '%s' successful."%(id))
                else:
                    raise Exception("Both catalog servers are down")    
        else:
            if app.config['catalogB_status'] == "UP":
                app.config['load_balancer_catalog'] = 0
                catalog_lock.release()
                app.logger.debug('Catalog B is up, Calling Catalog Server B')
                results=requests.get("%s/item/%s"%(CATALOG_SERVER_B["url"],id))
                app.logger.info("Searching of items with id '%s' successful."%(id))
            else:
                if app.config['catalogA_status'] == "UP":
                    app.config['load_balancer_catalog'] = 0
                    catalog_lock.release()
                    app.logger.debug('Catalog B is down, Calling Catalog Server A')
                    results=requests.get("%s/item/%s"%(CATALOG_SERVER_A["url"],id))
                    app.logger.info("Searching of items with id '%s' successful."%(id))
                else:
                    raise Exception("Both catalog servers are down")
        results=results.json()
        return results
    except requests.exceptions.ConnectionError as e:
        app.logger.info("Connection error, sending request to the other catalog server")
        try:
            if app.config['load_balancer_catalog'] == 1:
                app.logger.debug('Catalog A has crashed, Calling Catalog Server B')
                results = requests.get("%s/item/%s"%(CATALOG_SERVER_B["url"],id))
            else:
                app.logger.debug('Catalog B has crashed, Calling Catalog Server A')
                results = requests.get("%s/item/%s"%(CATALOG_SERVER_A["url"],id))
            results = results.json()
            return results
        except:
            app.logger.info("Failed to connect to the other catalog server. Error: %s" % (str(e)))
            return get_failed_response(message=str(e))
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return '%s Server shutting down...'%(str(sys.argv[3]))

if __name__=='__main__':
    start_heartbeats()
    app.run(host=str(sys.argv[1]), port=str(sys.argv[2]))
