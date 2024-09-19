import json, os
from flask import current_app
from bson.json_util import dumps
from app.services.update import UpdateService

def init_collections():
  print('COLLECTIONS CHECK')
  print('-----------------')
  existing_collections = current_app.mongo_db.list_collection_names()

  static_collections = ['commands','dusts','messages','qualities','wikiSchemas','levels', 'pipelines']

  for collec in static_collections:
    needs_update = None
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default', collec + '.json')
    
    with open(json_file, 'r', encoding='utf-8') as file:
      json_data = json.load(file)
    
    for item in json_data:
      if "_id" in item:
        del item["_id"]
    
    if collec in existing_collections:
      collection = current_app.mongo_db[collec]
      db_data = list(collection.find({}, {'_id': 0}))
        
      json_str = dumps(json_data, sort_keys=True)
      db_str = dumps(db_data, sort_keys=True)
        
      if json_str != db_str:
        print(f'  Collection {collec} différente du JSON...')
        collection.drop()
        needs_update = 'mise à jour'
      else:
        print(f'  Collection {collec} à jour')
    else:
      print(f'  Collection {collec} n\'existe pas...')
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
      
      print(f'  Collection {collec} {needs_update}')
  
  dynamic_collections = ['heroes','pets','talents']  
  dynamic_collections_names = ''
  need_to_create_dynamic_collections = False
  for i in range(0, len(dynamic_collections)):
    if i < len(dynamic_collections) - 1:
      dynamic_collections_names += dynamic_collections[i] + ' '
    else:
      dynamic_collections_names += '& ' + dynamic_collections[i]

    if dynamic_collections[i] not in existing_collections:
      need_to_create_dynamic_collections = True
  
  
  if need_to_create_dynamic_collections:
    print(f'  Collections {dynamic_collections_names} en cours de création...')
    UpdateService.update_all()
    print(f'  Collections créées')
  else:
    print(f'  Collections {dynamic_collections_names} déjà existantes')  