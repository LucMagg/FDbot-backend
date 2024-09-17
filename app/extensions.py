from pymongo import MongoClient

mongo_client = None

def init_mongo(app):
  global mongo_client
  app.mongo_client = MongoClient(app.config['MONGO_URI'])
  app.mongo_db = app.mongo_client[app.config['MONGO_DB_NAME']]