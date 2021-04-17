from flask import Flask
import requests 
from flask import request
from flask import jsonify
from response_util import get_failed_response,get_success_response 
import sys
sys.path.insert(1, '../')
# from const import CATALOG_SERVER, ORDER_SERVER
import logging
logging.basicConfig(filename="frontend.log", level=logging.DEBUG, format='%(asctime)s %(message)s', filemode='w')

app = Flask(__name__)

catalogA_url = str(sys.argv[3])
catalogB_url = str(sys.argv[4])
orderA_url = str(sys.argv[5])
orderB_url = str(sys.argv[6])

# defining the default page
@app.route('/', methods=['GET'])
def hello_world():
    return "Welcome to Book Store!. %s %s %s %s"%(catalogA_url, catalogB_url, orderA_url, orderB_url)

# the buy method which makes calls to the order server to buy an item based on provided item id
@app.route('/buy', methods=['GET'])
def buy():
    try:
        data = request.args
        id=data["id"]
        app.logger.info("Buy method called with the item with id '%s' in catalog server." % (id))
        results=requests.get("%s:%s/buy/%s"%(ORDER_SERVER["IP"],ORDER_SERVER["PORT"],id))
        results=results.json()
        app.logger.info("Purchase of item '%s' successfull."%(id))
        return results
    except Exception as e:
        app.logger.info("Failed to connect to order server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))


#the search method makes calls to the catalog server and searches for items based on topic name 
@app.route('/search',methods=['GET'])
def search():
    try:
        if 'topic' in request.args:
            topic=request.args['topic']
        else:
            return "Error: No topic field provided. Please specify a topic."
        app.logger.info("Search method called with the topic name '%s' in catalog server." % (topic))
        results=requests.get("%s:%s/item?topic=%s"%(CATALOG_SERVER["IP"],CATALOG_SERVER["PORT"],topic))
        app.logger.info("Searching of items with topic '%s' successful."%(topic))
        results=results.json()
        return results
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))


# the lookup method makes calls to the catalog server and searches for the item corresponding to item id
@app.route('/lookup',methods=['GET'])
def lookup():
    try:
        if 'id' in request.args:
            id=request.args['id']
        else:
            return "Error: No id field provided. Please specify an id."
        app.logger.info("Lookup method called with the id '%s' in catalog server." % (id))
        results=requests.get("%s:%s/item/%s"%(CATALOG_SERVER["IP"],CATALOG_SERVER["PORT"],id))
        results=results.json()
        app.logger.info("Looking Up of item with id '%s' successful."%(id))
        return results
        
    except Exception as e:
        app.logger.info("Failed to connect to catalog server. Error: %s" % (str(e)))
        return get_failed_response(message=str(e))

if __name__=='__main__':
    app.run(host=str(sys.argv[1]), port=str(sys.argv[2]))