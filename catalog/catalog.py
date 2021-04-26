from flask import Flask,request
import sqlite3
from pydantic import BaseModel
from response_util import get_failed_response,get_success_response
import json
import logging
import requests
import sys
sys.path.insert(1, '../')

catalog_url = str(sys.argv[4])

logging.basicConfig(filename=str(sys.argv[3])+".log",level=logging.DEBUG,
                    format='%(asctime)s %(message)s')
# logger=logging.getLogger()
log = logging.getLogger('werkzeug')
log.disabled = True

app = Flask(__name__)

class Book(BaseModel):
        id_:int = None    
        title:str = None
        count:int = None
        cost:int = None
        topic:str = None
        
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# con = sqlite3.connect('catalog.db')
# cur = con.cursor();
# cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='catalog';")
# response = cur.fetchone()
# if response == None:
#     cur.execute("create table IF NOT EXISTS catalog (id INTEGER PRIMARY KEY,title text,count INTEGER, cost INTEGER, topic text)")
#     sql_query ="INSERT INTO catalog(id,title,count,cost,topic) VALUES(?,?,?,?,?) "
#     values_1 = (1, 'How to get a good grade in 677 in 20 minutes a day.', 5, 10, 'distributed systems');
#     values_2 = (2, 'RPCs for Dummies.', 5, 10, 'distributed systems');
#     values_3 = (3, 'Xen and the Art of Surviving Graduate School.', 5, 10, 'graduate school');
#     values_4 = (4, 'Cooking for the Impatient Graduate Student.', 5, 10, 'graduate school');
#     values_5 = (5, 'How to finish Project 3 on time', 5, 10, 'distributed systems');
#     values_6 = (6, 'Why theory classes are so hard.', 5, 10, 'graduate school');
#     values_7 = (7, 'Spring in the Pioneer Valley', 5, 10, 'graduate school');
#     cur.execute(sql_query,values_1)
#     cur.execute(sql_query,values_2)
#     cur.execute(sql_query,values_3)
#     cur.execute(sql_query,values_4)
#     cur.execute(sql_query,values_5)
#     cur.execute(sql_query,values_6)
#     cur.execute(sql_query,values_7)
# con.commit()
# con.close()

try:
    app.logger.info("restarting after a crash")
    r = requests.get(catalog_url+"/item")
    r=r.json()
    app.logger.info("got request")
    con = sqlite3.connect('catalog.db')
    cur = con.cursor()
    cur.execute("drop table if exists catalog ;")
    app.logger.info("dropped table")
    cur.execute("create table IF NOT EXISTS catalog (id INTEGER PRIMARY KEY,title text,count INTEGER, cost INTEGER, topic text)")
    sql_query ="INSERT INTO catalog(id,title,count,cost,topic) VALUES(?,?,?,?,?) "
    values=[]
    for d in r["item"]:
        #looping over dictionaries
        values.append((d["id"],d["title"],d["count"],d["cost"],d["topic"]))
    for i in range(len(values)):
        cur.execute(sql_query,values[i])
    con.commit()
    con.close()
except:
    con = sqlite3.connect('catalog.db')
    cur = con.cursor();
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='catalog';")
    response = cur.fetchone()
    if response == None:
        cur.execute("create table IF NOT EXISTS catalog (id INTEGER PRIMARY KEY,title text,count INTEGER, cost INTEGER, topic text)")
        sql_query ="INSERT INTO catalog(id,title,count,cost,topic) VALUES(?,?,?,?,?) "
        values_1 = (1, 'How to get a good grade in 677 in 20 minutes a day.', 5, 10, 'distributed systems');
        values_2 = (2, 'RPCs for Dummies.', 5, 10, 'distributed systems');
        values_3 = (3, 'Xen and the Art of Surviving Graduate School.', 5, 10, 'graduate school');
        values_4 = (4, 'Cooking for the Impatient Graduate Student.', 5, 10, 'graduate school');
        values_5 = (5, 'How to finish Project 3 on time', 5, 10, 'distributed systems');
        values_6 = (6, 'Why theory classes are so hard.', 5, 10, 'graduate school');
        values_7 = (7, 'Spring in the Pioneer Valley', 5, 10, 'graduate school');
        cur.execute(sql_query,values_1)
        cur.execute(sql_query,values_2)
        cur.execute(sql_query,values_3)
        cur.execute(sql_query,values_4)
        cur.execute(sql_query,values_5)
        cur.execute(sql_query,values_6)
        cur.execute(sql_query,values_7)
    con.commit()
    con.close()

@app.route('/')
def catalog():
    
    '''
    DB initialization code below
    Uncomment to re-initialize the database
    '''
    
    return 'Hello, catalog!'

'''
item route is used for search, lookup and update.
There are 4 cases which are overall covered here - 
1. item route with an id_, method  = ['GET']
    Returns the item for the corresponding id
2. item route with a topic parameter in the query parameters, method  = ['GET']
    Returns the items for the corresponding topic
3. item route with no id and no payload, method  = ['GET']
    Returns the list of the items in the catalog database
4. item route with an id_,update payload, method  = ['PUT']
    Updates the item having id=id_ with the update data passed in payload.
    The update data contains fields 'cost' and 'count' to update the cost 
    and count of the entry with id=id_. Note that the cost update is direct 
    whereas the count update is addtional in nature since the order server 
    will pass the number of books which the frontend wants to buy.
'''


@app.route("/item/<id_>",methods = ['GET'])
@app.route("/item",methods = ['GET'])
def item(id_ = None):
    try:
        con = sqlite3.connect('catalog.db',timeout=30.0)
        con.row_factory = dict_factory
        cur = con.cursor()
        sql_query = ""
        if id_ == None:
            if request.args.get('topic') != None:
                app.logger.info("Looking up the items with topic '%s' in catalog database." % (request.args.get('topic')))
                sql_query ="select * from catalog where topic = ?;"
                values = (request.args.get('topic'),)
            else:
                app.logger.info("Looking up the all the items in the catalog database.")
                sql_query = "select * from catalog"
                values = ()
        else:
            app.logger.info("Looking up the item with id '%s' in catalog database." % (id_))
            sql_query ="select * from catalog where id = ?;"
            values = (id_,)
        cur.execute(sql_query,values)
        response = cur.fetchall()
        if response != None:
            app.logger.info("Lookup Successful")
        con.commit()
        con.close()
        return get_success_response('item',response,status_code = 200)
    except Exception as e:
        return get_failed_response(message=str(e))
    

@app.route("/item/<id_>",methods = ['PUT'])
def update_by_id(id_):
    try:
        con = sqlite3.connect('catalog.db',timeout=30.0)
        con.row_factory = dict_factory
        cur = con.cursor()
        sql_query ="select * from catalog where id = ?;"
        select_values = (id_,)
        app.logger.info("Looking up the item with id '%s' in catalog database for updating the item." % (id_))
        cur.execute(sql_query,select_values)
        response = cur.fetchone()
        data = json.loads(request.data)

        if 'count' in data:
            app.logger.info("Updating the count of item %s" % (id_))
            count = data['count']
            if count < 0:
                sign = "-"
                count = count*(-1)
                sql_query = "UPDATE catalog SET count = count %s %s where id = %s AND count > 0;" % (sign, count, id_)
                cur.execute(sql_query) 
                payload = {"count" : -count}
                app.logger.info("Propagating the count of item %s" % (id_))
                r = requests.put(catalog_url+"/item/propagate/%s"%(id_), data = json.dumps(payload))
            else:
                sign = "+"
                sql_query = "UPDATE catalog SET count = count %s %s where id = %s;" % (sign, count, id_)
                cur.execute(sql_query) 
                payload = {"count" : count}
                app.logger.info("Propagating the count of item %s" % (id_))
                r = requests.put(catalog_url+"/item/propagate/%s"%(id_), data = json.dumps(payload))

        if 'cost' in data:
            app.logger.info("Updating the cost of item %s" % (id_))
            sql_query = "UPDATE catalog SET cost = %s where id = %s;"%(data['cost'], id_)
            cur.execute(sql_query)
            payload = {"cost" : data['cost']}
            app.logger.info("Propagating the cost of item %s" % (id_))
            r = requests.put(catalog_url+"/item/propagate/%s"%(item_id), data = json.dumps(payload))
        con.commit()
        con.close()
        app.logger.info('Catalog database update successful')
        return get_success_response('item',{}, status_code=201)
    
    except Exception as e:
        return get_failed_response(message=str(e))

@app.route("/item/propagate/<id_>",methods = ['PUT'])
def propagate_by_id(id_):
    try:
        con = sqlite3.connect('catalog.db',timeout=30.0)
        con.row_factory = dict_factory
        cur = con.cursor()
        sql_query ="select * from catalog where id = ?;"
        select_values = (id_,)
        app.logger.info("Looking up the item with id '%s' in catalog database for updating the item." % (id_))
        cur.execute(sql_query,select_values)
        response = cur.fetchone()
        data = json.loads(request.data)

        if 'count' in data:
            app.logger.info("Updating the count of item %s" % (id_))
            count = data['count']
            if count < 0:
                sign = "-"
                count = count*(-1)
                sql_query = "UPDATE catalog SET count = count %s %s where id = %s AND count > 0;" % (sign, count, id_)
                cur.execute(sql_query) 
            else:
                sign = "+"
                sql_query = "UPDATE catalog SET count = count %s %s where id = %s;" % (sign, count, id_)
                cur.execute(sql_query) 

        if 'cost' in data:
            app.logger.info("Updating the cost of item %s" % (id_))
            sql_query = "UPDATE catalog SET cost = %s where id = %s;"%(data['cost'], id_)
            cur.execute(sql_query)
           
        con.commit()
        con.close()
        app.logger.info('Catalog database update successful')
        return get_success_response('item',{}, status_code=201)
    
    except Exception as e:
        return get_failed_response(message=str(e))

if __name__=='__main__':
    app.run(host=str(sys.argv[1]), port=str(sys.argv[2]))
