# -*- coding: utf-8 -*-
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
import pexpect
import pexpect.popen_spawn
import argparse
import requests
import json
import random
import logging
from const import FRONTEND_SERVER, CATALOG_SERVER, ORDER_SERVER, CATALOG_ITEMS, BOOK_TOPICS
servers = [FRONTEND_SERVER, CATALOG_SERVER, ORDER_SERVER]

##Initializing logger object
logging.basicConfig(filename="client.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

# Construct the argument parser
ap = argparse.ArgumentParser()
# Add the arguments to the parser
ap.add_argument("-pem", "--pemfile", required=False,
   help="Provide RSA Private key file")
ap.add_argument("-n", "--times", required=False,
   help="Provide the number of times you want to run the look,search and buy methods.")

args = vars(ap.parse_args())

# Marking the pem file location from the argument passed
pem_file = ""
if args['pemfile']:
    print("The pem file passed is %s" % (args['pemfile']))
    pem_file = args['pemfile']

def deploy_servers(pem_file):
    for server in servers:
        if server['IP'] not in ["http://localhost", "http://127.0.0.1", "http://0.0.0.0"]:

            if pem_file == '':
                raise("Provide the PEM file to run the remote commands. usage: runme.py [-h] [-pem PEMFILE] [-n NETWORK] [-k KILL] [-t TIME]")

            server['user_name'] = 'ec2-user'
            server_ip = server['IP'].split("//")[1]
        
            command = r'ssh -i '+ pem_file + ' ' + server['user_name'] + '@' + server_ip
            child = pexpect.popen_spawn.PopenSpawn(command)
            try:
                child.expect('$')
            except Exception as e:
                print("Log in failed for the remote server %s.")
                print("Please make sure the remote host is added to the known_hosts file in .ssh folder.")

            print("###### Deploying the code on the %s server: %s ######" % (server['type'], server_ip))
            child.sendline('mkdir src\n')
            child.expect("$")
            command2 = 'scp -i '+ pem_file +' -r * ' +server['user_name'] + '@' + server_ip+':/home/ec2-user/src/\n'
            time.sleep(5)        
            print(command2)
            os.system(command2)
            print("###### Successfully deployed the code on the %s server: %s ######" % (server['type'],server_ip))

            child.sendline('cd /home/ec2-user/src/%s\n'%(server['type']))
            child.expect('$')
            print('gunicorn -b 0.0.0.0:%s %s:app\n'%(server['PORT'], server['type']))
            child.sendline('gunicorn -b 0.0.0.0:%s %s:app\n'%(server['PORT'], server['type']))
            time.sleep(2)
            print("###### Successfully started the %s server ######" % (server['type']))
        else:
            subprocess.Popen("cd %s && python -m flask run -p %s"%(server['type'], server['PORT']), shell = True)
            print("###### Started the server %s on local machine ######" % (server['type']))

deploy_servers(pem_file)
time.sleep(5)

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
            return r.json()['order']
        else:
            logger.info("Buy of item '%s' failed with status_code: %s"%(item_id, r.status_code))
    except Exception as e:
        logger.info("Failed to connect to frontened server. Error: %s" % (str(e)))
        raise

##call to the frontend to search a particular topic
def frontend_search(topic):
    logger.info("Searching catalog server for the topic '%s'" % (topic_to_search))
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

#Default value of n=5
n=5
if args['times']:
    n = int(args['times'])
print("Running %s requests for lookup, search and buy"%(n))
print("Check out the ./client.log for more pass/fail logs.")
for i in range(n):
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
    logger.info("---------------------------------------------------------")
    time.sleep(2)
print("Process Complete.")

