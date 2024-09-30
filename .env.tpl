MONGODB_USER = 'your_MongoDB_username'
MONGODB_PWD = 'your_MongoDB_password'
MONGODB_CLUSTER = 'your_cluster_URL_(clustername.xxx.mongodb.net)'
MONGODB_DB = 'your_mongoDB_database_name'
MONGODB_BACKUP_DB = 'your_mongoDB_backup_database_name'


DAYS_OF_BACKUP_RETENTION = 15 # number of days for the db backups retention
BACKUP_MAX_RETRIES = 5 # number of retries if backup fails
BACKUP_RETRY_DELAY = 5 # backup retry delay in minutes
BACKUP_HOUR = 2 # backup hour
BACKUP_MINUTE = 0 # backup minute


HOST = 'your_backend_url_or_IP'
PORT = 0 # a number between 1024 and 49151