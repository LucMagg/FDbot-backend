import os
from app import create_app
from dotenv import load_dotenv

load_dotenv()

env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
  app.run(host = os.getenv('HOST'), port = os.getenv('PORT'))