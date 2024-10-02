import os
from dotenv import load_dotenv

class Config:
  load_dotenv()
  MONGO_URI = f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PWD')}@{os.getenv('MONGODB_CLUSTER')}"  
  MONGO_DB_NAME = os.getenv('MONGODB_DB')
  MONGO_DB_BACKUP = os.getenv('MONGODB_BACKUP_DB')

  DAYS_OF_BACKUP_RETENTION = int(os.getenv('DAYS_OF_BACKUP_RETENTION'))
  BACKUP_MAX_RETRIES = int(os.getenv('BACKUP_MAX_RETRIES'))
  BACKUP_RETRY_DELAY = int(os.getenv('BACKUP_RETRY_DELAY'))
  BACKUP_HOUR = int(os.getenv('BACKUP_HOUR'))
  BACKUP_MINUTE = int(os.getenv('BACKUP_MINUTE'))

  HOST = os.getenv('HOST')
  PORT = int(os.getenv('PORT'))

  LOG_FILE = os.getenv('LOG_FILE')


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