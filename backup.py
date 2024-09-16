from flask import current_app
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone

def need_backup(backup_db):
  backup_info = backup_db.backup_infos.find_one()
  if backup_info:
    last_backup_time = backup_info['last_backup']
    if datetime.now() - last_backup_time < timedelta(minutes=5):
      return False
  return True

def update_backup_info(backup_db):
  backup_db.backup_infos.update_one(
    {},
    {'$set': {'last_backup': datetime.now()}},
    upsert=True
  )

def backup_my_db():
  time = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
  print(f"{os.getenv('HOST')} - - [{time}] Vérification du backup de la database")

  try:
    source_db = current_app.mongo_db
    backup_db = current_app.backup_db

    if not need_backup(backup_db):
      print("  Backup récent détecté, skip du process :)")
      return

    print("  Début du backup de la database")
    update_backup_info(backup_db)

    collections = source_db.list_collection_names()

    for collection_name in collections:
      print(f"  Sauvegarde de la collection : {collection_name}")
      backup_db.drop_collection(collection_name)
      source_collection = source_db[collection_name]
      backup_collection = backup_db[collection_name]
      
      documents = list(source_collection.find())
      if documents:
        backup_collection.insert_many(documents)

    print(f" * Sauvegarde terminée avec succès")
  except Exception as e:
    print(f"Erreur lors de la sauvegarde : {e}")

scheduler = None
is_backup_done = False

def init_backup(app):
  global scheduler, is_backup_done
  if scheduler is None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=backup_my_db, trigger="interval", hours=24)
    scheduler.start()
  
  if not is_backup_done:
    with app.app_context():
      backup_my_db()
      is_backup_done = True

