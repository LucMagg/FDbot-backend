import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

def need_backup(db_names: list):
  today = datetime.now().strftime('%d-%m-%y')
  for db_name in db_names:
    if today in db_name:
      return False
  return True

def delete_old_and_corrupted_backups(db_names: list, app):
  for db in db_names:
    if '_' in db:
      db_date = datetime.strptime(db.split('_')[-1], '%d-%m-%y')
      if datetime.now() - db_date > timedelta(days=int(app.config['DAYS_OF_BACKUP_RETENTION'])):
        app.mongo_client.drop_database(db)
        print(f"  Backup expiré ({db}) : suppression...")
    else:
      app.mongo_client.drop_database(db)
      print(f"  Backup incohérent détecté ({db}) : suppression...")

def backup_my_db(app):
  time = datetime.now().strftime('%d/%b/%Y %H:%M:%S')
  print(f"{os.getenv('HOST')} - - [{time}] Vérification du backup de la database")

  backup_database_names = [db for db in app.mongo_client.list_database_names() if app.config['MONGO_DB_BACKUP'] in db]
  delete_old_and_corrupted_backups(backup_database_names, app)

  if not need_backup(backup_database_names):
    print("  Backup déjà effectué aujourd'hui :)")
    return

  try:
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
  except Exception as e:
    print(f"Erreur lors de la sauvegarde : {e}")

scheduler = None
is_backup_done = False

def init_backup(app):
  global scheduler, is_backup_done
  if scheduler is None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: backup_my_db(app), trigger="cron", hour=2, minute=0)
    scheduler.start()
  
  if not is_backup_done:
    with app.app_context():
      backup_my_db(app)
      is_backup_done = True