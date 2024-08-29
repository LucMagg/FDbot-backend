import os
from app import create_app
from dotenv import load_dotenv # type: ignore

load_dotenv()

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(host = os.getenv('HOST'), port = os.getenv('PORT'))