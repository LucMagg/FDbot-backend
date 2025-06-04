import json, os
from flask import current_app
from bson.json_util import dumps
from app.services.update import UpdateService

def init_collections():
  current_app.logger.back_log('COLLECTIONS CHECK')
  existing_collections = current_app.mongo_db.list_collection_names()

  static_collections = ['commands','dusts','messages','qualities','wikiSchemas', 'pipelines', 'rewardTypes', 'rewardChoices', 'heroXp', 'xpThresholds'] #, 'maps'] #<-- Ajouter maps pour créer la collection à partir du json stocké

  for collec in static_collections:
    needs_update = None
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default', collec + '.json')
    
    with open(json_file, 'r', encoding='utf-8') as file:
      json_data = json.load(file)
    
    if collec in existing_collections:
      collection = current_app.mongo_db[collec]
      db_data = list(collection.find({}))
        
      if not compare_collections(json_data, db_data):
        current_app.logger.back_log(f'  Collection {collec} différente du JSON...')
        collection.drop()
        needs_update = 'mise à jour'
      else:
        current_app.logger.back_log(f'  Collection {collec} à jour')
    else:
      current_app.logger.back_log(f'  Collection {collec} n\'existe pas...')
      needs_update = 'créée'
    
    if needs_update:
      collection = current_app.mongo_db[collec]
        
      if isinstance(json_data, list):
        for item in json_data:
          item.pop('_id', None)
        collection.insert_many(json_data)
      else:
        json_data.pop('_id', None)
        collection.insert_one(json_data)
      
      current_app.logger.back_log(f'  Collection {collec} {needs_update}')
  
  dynamic_collections = ['heroes','pets','talents']  
  dynamic_collections_names = ' & '.join(dynamic_collections)
  need_to_create_dynamic_collections = any(coll not in existing_collections for coll in dynamic_collections)
    
  if need_to_create_dynamic_collections:
    current_app.logger.back_log(f'  Collections {dynamic_collections_names} en cours de création...')
    UpdateService.update_all()
    current_app.logger.back_log(f'  Collections créées')
  else:
    current_app.logger.back_log(f'  Collections {dynamic_collections_names} déjà existantes')

def compare_collections(json_data, db_data):
  if len(json_data) != len(db_data):
    return False
        
  json_docs = [normalize_document(doc) for doc in json_data]
  db_docs = [normalize_document(doc) for doc in db_data]
  
  sort_key = next((k for k in ['name_slug', 'name', 'hero_stars'] if json_docs and k in json_docs[0].keys()), '')
  json_docs.sort(key=lambda x: x.get(sort_key, ''))
  db_docs.sort(key=lambda x: x.get(sort_key, ''))

  return all(dumps(j, sort_keys=True) == dumps(d, sort_keys=True) for j, d in zip(json_docs, db_docs))

def normalize_document(doc):
  if not isinstance(doc, (dict, list)):
    return doc
        
  if isinstance(doc, dict):
    normalized = {}
    for key, value in sorted(doc.items()):
      if key != '_id':
        normalized[key] = normalize_document(value)
    return normalized
      
  if isinstance(doc, list):
    return [normalize_document(item) for item in doc]