from flask import current_app

class GearService:

  @staticmethod
  def get_gear(type=None, position=None):   
    pipeline_doc = current_app.mongo_db.pipelines.find_one({'name': 'unique_gear'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        if 'gear.position' in stage['$match'].keys():
          if position:
            if isinstance(position, list):
              stage['$match']['gear.position'] = {"$in": position}
            else:
              stage['$match']['gear.position'] = position
          else:
            del stage['$match']['gear.position']
        if 'type' in stage['$match'].keys():
          if type:
            if isinstance(type, list):
              stage['$match']['type'] = {"$in": type}
            else:
              stage['$match']['type'] = type
          else:
            del stage['$match']['type']

    gear = list(current_app.mongo_db.heroes.aggregate(pipeline_stages))

    for g in gear:
      if 'Melee/Ranged' in g['types']:
        if 'Melee' not in g['types']:
          g['types'].append('Melee')
        g['types'].remove('Melee/Ranged')
    return gear
  
  @staticmethod
  def get_all_gear():   
    pipeline_doc = current_app.mongo_db.pipelines.find_one({'name': 'list_all_gear'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    gear = list(current_app.mongo_db.heroes.aggregate(pipeline_stages))

    return gear