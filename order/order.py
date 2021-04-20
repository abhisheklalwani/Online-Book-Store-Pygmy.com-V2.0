# from application import app
from flask import Flask, render_template, request, Response, json, redirect, flash, url_for, session, Markup, jsonify
from config import Config
from response_util import get_failed_response, get_success_response
import requests
from datetime import datetime
import sys
sys.path.insert(1, '../')
import logging
logging.basicConfig(filename=str(sys.argv[3])+".log", level=logging.DEBUG, format='%(asctime)s %(message)s %(threadName)s')

# order 1 contacts catalog 1

catalog_url = str(sys.argv[5])
order_url= str(sys.argv[4])

app = Flask(__name__)
# app.config.from_object(Config)
log = logging.getLogger('werkzeug')
log.disabled = True

from sqlite_db import order

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return {"response": "Hi! You have reached the order server."}

@app.route('/orders')
def orders():
    order_db = order()
    orders = order_db.get_orders()
    return get_success_response('order', orders)

@app.route('/buy/<item_id>', methods = ['GET'])
def buy(item_id = None):
    app.logger.info("Recieved a buy request of the item %s" % (item_id))
    if not item_id:
        get_failed_response(message = "Item id has to be passed for buying.", status_code = 400)
    order_db = order()
    
    ##Check wether the item id is there in the catalog server
    r = requests.get(catalog_url+"/item/%s"%(item_id))
    if r.status_code == 200:
        #get the item 
        item = r.json()['item']
        if item:
            item_count = r.json()['item'][0]['count']
        else:
            return get_failed_response(status_code = 404, message =  "Item with id %s not found in the catalog server." % (item_id))
    else:
        return get_failed_response(message = "Couldn't fetch item status from the catalog server.")

    #If present issue a update request to the catalog server
    if item_count>0:
        app.logger.info("Item with id %s present in the catalog server. Going ahead to buy it" % (item_id))
        payload = {"count" : -1}
        r = requests.put(catalog_url+"/item/%s"%(item_id), data = json.dumps(payload))
        if r.status_code != 201:
            app.logger.error("Error: %s" % (str(r.json())))
            return get_failed_response(message = "Failed to update catalog server.")

        app.logger.info("Successfully bought the item %s from the catalog server." % (item_id))
        #propagating update
        order_id = order_db.add_order({'item_id': item_id, 'created':  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))})
        payload_order={"update":{'item_id': item_id, 'created':  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}}
        app.logger.info("Propagating update to order database")
        r = requests.put(order_url, data = json.dumps(payload_order))
        return get_success_response("order", output = {'id': order_id}, message = "Item with id %s bought successfully." % (item_id))
    else:
        app.logger.info("The item with id %s is no longer present in the catalog server. Restocking the catalog server" % (item_id))
        payload = {"count": 10}
        r = requests.put(catalog_url+"/item/%s"%(item_id), data = json.dumps(payload))
        if r.status_code != 201:
            app.logger.error("Error: %s" % (str(r.json())))
            return get_failed_response(message = "Failed to update catalog server.")
        return get_failed_response(message = "The item with id %s is no longer present in the catalog server" % (item_id), status_code = 404)

@app.route('/update', methods = ['PUT'])
def add_to_order():
    order_db = order()
    data = json.loads(request.data)
    order_update=data["update"]
    order_id = order_db.add_order(order_update)
    app.logger.info("Propagated update to database")
    return get_success_response("succesfully updated order id %s" %(order_id))

if __name__=='__main__':

    app.run(host=str(sys.argv[1]), port=str(sys.argv[2]))
