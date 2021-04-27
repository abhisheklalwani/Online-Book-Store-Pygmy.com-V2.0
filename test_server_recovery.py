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

CATALOGA_SERVER = {'IP': sys.argv[1], 'PORT': sys.argv[2]}
CATALOGB_SERVER = {'IP': sys.argv[3], 'PORT': sys.argv[4]}

##Initializing logger object
logging.basicConfig(filename="test_server_recovery.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

def item_lookup(server):
    logger.info("Looking up the items in catalog server %s." % (server['IP']))
    try:
        r = requests.get("%s:%s/item"%(server["IP"],server["PORT"]))
        if r.status_code == 200:
            logger.info("GET of items successfull.")
            return r.json()['item']
        else:
            logger.info("GET of items failed with status_code: %s"%(r.status_code))

    except Exception as e:
        logger.info("Failed to connect to catalog server %s. Error: %s" % (server["IP"], str(e)))
        raise

logger.info("Getting items from the catalogA server")
itemsA = item_lookup(CATALOGA_SERVER)
logger.info("Getting items from the catalogB server")
itemsB = item_lookup(CATALOGB_SERVER)

# Checking if both the items that are same to check the resyn functionality
try:
	for itemA in itemsA:
		idA = itemA['id']
		for itemB in itemsB:
			if itemB['id'] == idA:
				##Checking if the values are in sync
				for attr in itemA:
					logger.debug("Checking the %s of item with id %s in both the servers." % (attr, idA))
					if itemA[attr] != itemB[attr]:
						raise "The %s of both the catalog servers are not matching for the item with id %s" % (attr, idA)
			break
	logger.info("Test complete. Both the catlaog servers are in sync.")
except Exception as e:
	logger.error(str(e))

