#-*- coding: utf-8 -*-
"""
Created on Wed Mar  3 16:05:24 2021
@author: Himanshu , Kunal, Abhishek 
"""

#importing libraries
import os
import subprocess
import time
import sys
import re
import requests
import json
import random
import logging
import multiprocessing

FRONTEND_SERVER = {'IP': sys.argv[1], 'PORT': sys.argv[2]}

from const import CATALOG_ITEMS, BOOK_TOPICS

##Initializing logger object
logging.basicConfig(filename="client.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

##call to frontend server to lookup for a particular item
def frontend_lookup(item_id):
    logger.info("Looking up the item with id '%s' in frontend server." % (item_id))
    try:
        r = requests.get("%s:%s/lookup?id=%s"%(FRONTEND_SERVER["IP"],FRONTEND_SERVER["PORT"],item_id))
        if r.status_code == 200:
            logger.info("Lookup of item '%s' successfull."%(item_id))
            return r.json()['item'][0]['count']>0
        else:
            logger.info("Lookup of item '%s' failed with status_code: %s"%(item_id, r.status_code))

    except Exception as e:
        logger.info("Failed to connect to frontened server. Error: %s" % (str(e)))
        raise

##call to frontend to buy a particular item
def order_buy(item_id):
    logger.info("Buying the item with id '%s' from front server." % (item_id))
    try:
        r = requests.get("%s:%s/buy?id=%s"%(FRONTEND_SERVER["IP"],FRONTEND_SERVER["PORT"],item_id))
        if r.status_code == 200:
            logger.info("Succesfully bought the item '%s'" % (item_id))
            # return r.json()['order']
        else:
            logger.info("Buy of item '%s' failed with status_code: %s"%(item_id, r.status_code))
    except Exception as e:
        logger.info("Failed to connect to frontened server. Error: %s" % (str(e)))
        raise

##call to the frontend to search a particular topic
def frontend_search(topic):
    logger.info("Searching catalog server for the topic '%s'" % (topic))
    try:
        r = requests.get("%s:%s/search?topic=%s"%(FRONTEND_SERVER["IP"],FRONTEND_SERVER["PORT"],topic))
        status_code = r.status_code
        if status_code == 200:
            logger.info("Search of topic '%s' successfull."%(topic))
            return r.json()['item']
        else:
            logger.info("Search of topic '%s' failed with status_code: %s"%(topic, status_code))
    except Exception as e:
        logger.info("Failed to connect to frontened server. Error: %s" % (str(e)))
        raise

def client_call(client_id):
    logger.info('Calling client with client_id = %s'%client_id)
    for i in range(1):
        ##selecting a random topic to search
        index = random.randint(0,len(BOOK_TOPICS)-1)
        topic_to_search = BOOK_TOPICS[index]

        #getting all the items with a particular topic
        items = frontend_search(topic_to_search)

        ##taking a random item from the list and checking the presence of the same in the server
        item_to_lookup = items[random.randint(0,len(items)-1)]
        id_ = item_to_lookup['id']
        item_present = frontend_lookup(id_)

        ##if item is present, call the order server to buy the particular item
        if item_present:
            item_bought=order_buy(id_)
        else:
            logger.info("Item with id '%s' got finished in the server." % (id_))

if __name__ == "__main__":
    #Default value of n=5
    n = int(sys.argv[3])
    print("Setting up %s clients for testing the systems. They will call lookup, search and buy methods of the frontend server 10 times."%(n))
    print("Please wait. This step will take a few minutes to run.")
    print("Check out the ./client.log for final pass/fail logs.")

    for i in range(10):
        processes = []
    
        for i in range(n):
            processes.append(multiprocessing.Process(target=client_call, args=(i, )))
        for process in processes:
            process.start()
        for process in processes:
            process.join()

        print('Iteration ',i+1,' Complete.')
    
    print('Process Completed. Please refer to logs to check the results of the run.') 

