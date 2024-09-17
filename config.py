import os
from dotenv import load_dotenv

class Config:
  load_dotenv()
  MONGO_URI = f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PWD')}@{os.getenv('MONGODB_CLUSTER')}"  
  MONGO_DB_NAME = os.getenv('MONGODB_DB')
  MONGO_DB_BACKUP = os.getenv('MONGODB_BACKUP_DB')
  DAYS_OF_BACKUP_RETENTION = os.getenv('DAYS_OF_BACKUP_RETENTION')

class DevelopmentConfig(Config):
  DEBUG = True


class TestingConfig(Config):
  TESTING = True


class ProductionConfig(Config):
  DEBUG = False


config = {
  'development': DevelopmentConfig,
  'testing': TestingConfig,
  'production': ProductionConfig,
  'default': DevelopmentConfig
}