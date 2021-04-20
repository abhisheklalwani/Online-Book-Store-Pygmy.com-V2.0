from flask import Flask,session
from flask_session import Session
import requests 
from flask import request
from flask import jsonify
from response_util import get_failed_response,get_success_response 
import sys
from flask_caching import Cache
# sys.path.insert(1, '../')
import logging

logging.basicConfig(filename="frontend.log", level=logging.DEBUG, format='%(asctime)s %(message)s', filemode='w')

config = {          
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 0
}

app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

app.config.from_mapping(config)
cache = Cache(app)

CATALOG_SERVER_A = {"type": "catalog", "url": str(sys.argv[3])}
CATALOG_SERVER_B = {"type": "catalog", "url": str(sys.argv[4])}
ORDER_SERVER_A = {"type": "order", "url": str(sys.argv[5])}
ORDER_SERVER_B = {"type": "order", "url": str(sys.argv[6])}

# defining the default page
@app.route('/', methods=['GET'])
def hello_world():
    session['load_balancer_catalog'] = 0
    session['load_balancer_order'] = 0
    return "Welcome to Book Store!"

# the buy method which makes calls to the order server to buy an item based on provided item id
@app.route('/buy', methods=['GET'])
def buy():
    try:
        data = request.args
        id=data["id"]
        app.logger.info("Buy method called with the item with id '%s' in catalog server." % (id))
        if session['load_balancer_order'] == 0:
            session['load_balancer_order'] = 1
            results=requests.get("%s/buy/%s"%(ORDER_SERVER_A["url"],id))
            results=results.json()
        else:
            session['load_balancer_order'] = 0
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
@cache.cached(key_prefix='topic_lookup')
def search():
    app.logger.info("%s,%s,%s,%s"%(CATALOG_SERVER_A["url"], CATALOG_SERVER_B["url"], ORDER_SERVER_A["url"], ORDER_SERVER_B["url"]))
    try:
        if 'topic' in request.args:
            topic=request.args['topic']
        else:
            return "Error: No topic field provided. Please specify a topic."
        app.logger.info("Search method called with the topic name '%s' in catalog server." % (topic))
        if session['load_balancer_catalog'] == 0:
            session['load_balancer_catalog'] = 1
            app.logger.info("%s/item?topic=%s"%(CATALOG_SERVER_A["url"],topic))
            results=requests.get("%s/item?topic=%s"%(CATALOG_SERVER_A["url"],topic))
            app.logger.info("Searching of items with topic '%s' successful."%(topic))
        else:
            session['load_balancer_catalog'] = 0
            results=requests.get("%s/item?topic=%s"%(CATALOG_SERVER_B["url"],topic))
            app.logger.info("Searching of items with topic '%s' successful."%(topic))
        results=results.json()
        return results
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))


# the lookup method makes calls to the catalog server and searches for the item corresponding to item id
@app.route('/lookup',methods=['GET'])
@cache.cached(key_prefix='id_lookup')
def lookup():
    try:
        if 'id' in request.args:
            id=request.args['id']
        else:
            return "Error: No id field provided. Please specify an id."
        app.logger.info("Lookup method called with the id '%s' in catalog server." % (id))
        if session['load_balancer_catalog'] == 0:
            session['load_balancer_catalog'] = 1
            results=requests.get("%s/item/%s"%(CATALOG_SERVER_A["url"],id))
            results=results.json()
        else:
            session['load_balancer_catalog'] = 0
            results=requests.get("%s/item/%s"%(CATALOG_SERVER_B["url"],id))
            results=results.json()
        app.logger.info("Looking Up of item with id '%s' successful."%(id))
        return results
        
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))

if __name__=='__main__':
    app.run(host=str(sys.argv[1]), port=str(sys.argv[2]))
