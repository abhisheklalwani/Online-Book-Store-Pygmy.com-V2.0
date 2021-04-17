# FRONTEND_SERVER = {"type": "frontend", "IP": "http://3.83.164.236", "PORT": 8010}
# CATALOG_SERVER = {"type": "catalog", "IP": "http://54.234.162.97", "PORT": 8011}
# ORDER_SERVER = {"type": "order", "IP": "http://52.207.221.106", "PORT": 8012}

FRONTEND_SERVER = {"type": "frontend", "IP": "http://127.0.0.1", "PORT": 8010}
# CATALOG_SERVER = {"type": "catalog", "IP": "http://54.211.94.114", "PORT": 8011}
CATALOG_SERVERs = [{"tag": "catalogA", "type": "catalog", "IP": "http://127.0.0.1", "PORT": 8011}, {"tag": "catalogB", "type": "catalog", "IP": "http://127.0.0.1", "PORT": 8012}]
ORDER_SERVER = [{"tag": "orderA", "type": "order", "IP": "http://127.0.0.1", "PORT": 8013},  {"tag": "orderB", "type": "order", "IP": "http://127.0.0.1", "PORT": 8014}]
CATALOG_ITEMS = 5
BOOK_TOPICS = ["distributed systems", "graduate school"]