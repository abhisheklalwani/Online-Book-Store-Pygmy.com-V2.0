import sqlite3
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class order:
	def __init__(self):
		try:
			self.connection = sqlite3.connect("order_server.db")
		except Exception as e:
			print("Error in connecting to email_server.db. Error: %s" % (str(e)))
		# self.connection.row_factory = sqlite3.Row
		self.connection.row_factory = dict_factory
		self.cursor = self.connection.cursor()
		self.columns = ['id', 'item_id', 'created']
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY NOT NULL, item_id INTEGER NOT NULL, created date NOT NULL)''')

	def get_orders(self):
		sql_command = "SELECT * from orders;"
		self.cursor.execute(sql_command)
		orders = self.cursor.fetchall()
		return orders

	def get_order_by_id(self, order_id):
		self.cursor.execute("SELECT * FROM orders WHERE id=?", (order_id,))
		order = self.cursor.fetchone()
		return order

	def add_order(self, payload):
		email_tuple = (payload["item_id"], payload["created"],)
		sql_command = "INSERT INTO orders(item_id, created) VALUES (?, ?)"
		self.cursor.execute(sql_command, email_tuple)
		id = self.cursor.lastrowid
		self.connection.commit()
		return id

	def delete_order_by_id(self, order_id):
		self.cursor.execute("DELETE from orders WHERE id = ?", (order_id,))
		self.connection.commit()
	
	def delete_table(self):
		self.cursor.execute("drop table if exists orders ;")
		self.connection.commit()