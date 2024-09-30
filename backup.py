import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import datetime, timedelta
from filelock import FileLock

scheduler = None
is_backup_done = False
max_retries = 3
retry_delay = 5

def need_backup(db_names: list):
  today = datetime.now().strftime('%d-%m-%y')
  return not any(today in d for d in db_names)

def delete_old_and_corrupted_backups(db_names: list, app):
  for db in db_names:
    if '_' in db:
      db_date = datetime.strptime(db.split('_')[-1], '%d-%m-%y')
      if datetime.now() - db_date > timedelta(days=app.config['DAYS_OF_BACKUP_RETENTION']):
        app.mongo_client.drop_database(db)
        print(f"  Backup expiré ({db}) : suppression...")
    else:
      app.mongo_client.drop_database(db)
      print(f"  Backup incohérent détecté ({db}) : suppression...")

def backup_my_db(app):
  lock = FileLock("/tmp/backup.lock", timeout=10)

  try:
    with lock:
      time = datetime.now().strftime('%d/%b/%Y %H:%M:%S')
      print(f"{os.getenv('HOST')} - - [{time}] Vérification du backup de la database")

      backup_database_names = [db for db in app.mongo_client.list_database_names() if app.config['MONGO_DB_BACKUP'] in db]
      delete_old_and_corrupted_backups(backup_database_names, app)

      if not need_backup(backup_database_names):
        print("  Backup déjà effectué aujourd'hui :)")
        return True

      print("  Début du backup de la database")
      source_db = app.mongo_db
      backup_db_name = f"{app.config['MONGO_DB_BACKUP']}_{datetime.now().strftime('%d-%m-%y')}"
      backup_db = app.mongo_client[backup_db_name]

      collections = source_db.list_collection_names()

      for collection_name in collections:
        print(f"  Sauvegarde de la collection : {collection_name}")
        backup_db.drop_collection(collection_name)
        source_collection = source_db[collection_name]
        backup_collection = backup_db[collection_name]
        
        documents = list(source_collection.find())
        if documents:
          backup_collection.insert_many(documents)

      print(f" * Sauvegarde terminée avec succès dans la db : {backup_db_name}")
      return True
  except Exception as e:
    print(f"Erreur lors de la sauvegarde : {e}")
    return False

def job_listener(event):
  global is_backup_done
  if event.exception:
    print(f"Backup échoué. Exception: {event.exception}")
    is_backup_done = False
  else:
    print("Backup effectué avec suuccès :)")
    is_backup_done = True

def retry_backup(app):
  global is_backup_done, max_retries
  max_retries = app.config.get('BACKUP_MAX_RETRIES', 3)
  retry_delay = app.config.get('BACKUP_RETRY_DELAY', 5)

  for attempt in range(max_retries):
    if is_backup_done:
      break

    print(f"Tentative de backup {attempt + 1}/{max_retries}")
    with app.app_context():
      if backup_my_db(app):
        is_backup_done = True
        break
    
    if not is_backup_done and attempt < max_retries - 1: 
      scheduler.add_job(
        func=lambda: retry_backup(app),
        trigger="date",
        run_date=datetime.now() + timedelta(minutes=retry_delay),
        id=f'retry_backup_{attempt}'
      )
  if not is_backup_done:
    print(f"Le backup a échoué après {max_retries} tentatives. Veuillez vérifier le système.")

def init_backup(app):
  global scheduler, is_backup_done
  if scheduler is None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
      func=lambda: backup_my_db(app),
      trigger="cron",
      hour=app.config.get('BACKUP_HOUR', 2),
      minute=app.config.get('BACKUP_MINUTE', 0),
      id='daily_backup'
    )
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()
  
  if not is_backup_done:
    with app.app_context():
      retry_backup(app)