"""
from flask import Flask # type: ignore
from bson import json_util
from db import get_database
from json import loads


app = Flask(__name__)
db = get_database()

@app.route('/dusts', methods=['GET'])
def get_all_dusts():
  collection = db['dusts']
  dustList = collection.find()
  return loads(json_util.dumps(dustList))



if __name__ == '__main__':
  app.run(debug=True, port=8008)  
"""

import os
from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8008)