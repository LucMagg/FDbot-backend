from pymongo import MongoClient # type: ignore
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

mongodb_uri = f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PWD')}@{os.getenv('MONGODB_CLUSTER')}"
client = MongoClient(mongodb_uri)

def get_database():
  return client[os.getenv('MONGODB_DB')]