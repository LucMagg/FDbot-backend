from flask import current_app

def init_pipelines():
  heroes_by_class_pipeline = [
    {'$match': {'heroclass': '{{heroclass}}'}},
    {'$project': {
      '_id': 1,
      'name': 1,
      'heroclass': 1,
      'color': 1,
      'species': 1,
      'stars': 1,
      'talents': 1,
      'ascend_max': 1,
      'attack': 1,
      'defense': 1,
      'pet': 1
    }}
  ]

  heroes_by_gear_name_pipeline = [
    {'$match': {'gear': {'$exists': True, '$ne': []}}},
    {'$unwind': '$gear'},
    {'$match': {'gear.name': '{{gear_name}}'}},
    {'$group': {
      '_id': '$_id',
      'name': {'$first': '$name'},
      'gear': {'$push': {
        'ascend': '$gear.ascend',
        'quality': '$gear.quality'
      }},
      'heroclass': {'$first': '$heroclass'},
      'color': {'$first': '$color'},
      'stars': {'$first': '$stars'}
    }}
  ]

  heroes_by_gear_name_and_quality_pipeline = [
    {'$match': {'gear': {'$exists': True, '$ne': []}}},
    {'$unwind': '$gear'},
    {'$match': {'gear.name': '{{gear_name}}', 'gear.quality': '{{gear_quality}}'}},
    {'$project': {
      '_id': 1,
      'name': 1,
      'heroclass': 1,
      'color': 1,
      'stars': 1,
      'gear.ascend': 1
    }},
    {'$group': {
      '_id': '$_id',
      'name': {'$first': '$name'},
      'gear': {'$push': '$gear.ascend'},
      'heroclass': {'$first': '$heroclass'},
      'color': {'$first': '$color'},
      'stars': {'$first': '$stars'}
    }}
  ]

  heroes_by_talent_pipeline = [
    {'$match': {'talents': {'$exists': True, '$ne': []}}},
    {'$unwind': '$talents'},
    {'$match': {'talents.name': '{{talent_name}}'}},
    {'$project': {
      '_id': 1,
      'name': 1,
      'heroclass': 1,
      'color': 1,
      'stars': 1,
      'talents.position': 1
    }},
    {'$group': {
      '_id': '$_id',
      'name': {'$first': '$name'},
      'talents': {'$push': '$talents.position'},
      'heroclass': {'$first': '$heroclass'},
      'color': {'$first': '$color'},
      'stars': {'$first': '$stars'}
    }}
  ]

  heroes_by_pet_pipeline = [
    {'$match': {'color': '{{color}}', 'heroclass': '{{petclass}}'}},
    {'$project': {'name': 1}}
  ]

  list_all_classes_pipeline = [
    {'$group': {'_id': "$heroclass"}},
    {'$project': {
      '_id': 0,
      'heroclass': '$_id'
    }},
    {'$sort': {'heroclass': 1 }}
  ]

  pets_by_class_pipeline = [
    {'$match': {'petclass': '{{petclass}}'}},
    {'$project': {
      '_id': 1,
      'name': 1,
      'petclass': 1,
      'signature': 1,
      'signature_bis': 1,
      'color': 1,
      'stars': 1
    }}
  ]

  pets_by_talent_pipeline = [
    {'$match': {'talents': {'$exists': True, '$ne': []}}},
    {'$unwind': '$talents'},
    {'$match': {'talents.name': '{{talent_name}}'}},
    {'$project': {
      '_id': 1,
      'name': 1,
      'petclass': 1,
      'color': 1,
      'stars': 1,
      'talents.position': 1
    }},
    {'$group': {
      '_id': '$_id',
      'name': {'$first': '$name'},
      'talents': {'$push': '$talents.position'},
      'petclass': {'$first': '$petclass'},
      'color': {'$first': '$color'},
      'stars': {'$first': '$stars'}
    }}
  ]

  pets_by_color_or_heroname_pipeline = [
    {'$match': {
      '$or': [
        {'color': '{{color}}'},
        {'signature': '{{heroname}}'},
        {'signature_bis': '{{heroname}}'}
      ]
    }},
    {'$group': {
      '_id': '$_id',
      'pet': {'$first': '$$ROOT'}
    }},
    {'$replaceRoot': {'newRoot': '$pet'}}
  ]

  pipelines = [
    ['heroes_by_class', heroes_by_class_pipeline],
    ['heroes_by_gear_name', heroes_by_gear_name_pipeline],
    ['heroes_by_gear_name_and_quality', heroes_by_gear_name_and_quality_pipeline],
    ['heroes_by_talent', heroes_by_talent_pipeline],
    ['heroes_by_pet', heroes_by_pet_pipeline],
    ['list_all_classes', list_all_classes_pipeline],
    ['pets_by_class', pets_by_class_pipeline],
    ['pets_by_talent', pets_by_talent_pipeline],
    ['pets_by_color_or_heroname', pets_by_color_or_heroname_pipeline]
  ]

  print('PIPELINES CHECK')
  print('---------------')

  for p in pipelines:
    does_pipeline_exists(p[0], p[1])

def does_pipeline_exists(pipeline_name, pipeline_definition):
  db = current_app.mongo_db
  pipelines_collection = db.pipelines

  existing_pipeline = pipelines_collection.find_one({'name': pipeline_name})

  if not existing_pipeline:
    pipelines_collection.insert_one({
        'name': pipeline_name,
        'pipeline': pipeline_definition
    })
    print(f'  Aggregation pipeline {pipeline_name} created')
  else:
    print(f'  Aggregation pipeline {pipeline_name} already exists')