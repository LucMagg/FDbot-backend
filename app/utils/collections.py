import json, os
from flask import current_app
from app.services.update import UpdateService

def init_collections():
  print('COLLECTIONS CHECK')
  print('-----------------')
  existing_collections = current_app.mongo_db.list_collection_names()

  static_collections = ['commands','dusts','messages','qualities','wikiSchemas']

  for collec in static_collections:
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default', collec + '.json')
    
    if collec not in existing_collections:
      print(f'  Collection {collec} doesn\'t exist, creation in progress...')
      
      with open(json_file, 'r') as file:
        data = json.load(file)
      
      collection = current_app.mongo_db[collec]
      if isinstance(data, list):
        collection.insert_many(data)
      else:
        collection.insert_one(data)
      
      print(f'  Collection {collec} created')
    else:
      print(f'  Collection {collec} already exists')
  
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
    print(f'  Update collections {dynamic_collections_names}...')
    UpdateService.update_all()
    print(f'  Collections created')
  else:
    print(f'  Collections {dynamic_collections_names} already exist')  