from flask import current_app
from app.models.level import Level


class LevelService:

  @staticmethod
  def add_level(level_data):
    level = Level.from_dict(level_data)
    return level.create(current_app.mongo_db)

  @staticmethod
  def get_one_level(level_name):
    level_obj = Level.read_by_name(current_app.mongo_db, level_name)
    return level_obj if level_obj else None

  @staticmethod
  def get_all_levels():
    return Level.read_all(current_app.mongo_db)

  @staticmethod
  def add_reward(level_name, reward_data):
    level = Level.read_by_name(current_app.mongo_db, level_name)
    if level:
      return Level.add_reward(current_app.mongo_db, level.to_dict(), reward_data)
    return None
  
  def set_new_reward_types():
    return Level.build_new_levels(current_app.mongo_db)
  
  @staticmethod
  def get_level_by_gear(item: str, quality: str = None):
    if quality is None:
      pipeline_doc = current_app.mongo_db.pipelines.find_one({'name': 'levels_by_gear_name'})
    else:
      pipeline_doc = current_app.mongo_db.pipelines.find_one({'name': 'levels_by_gear_name_and_quality'})
    if not pipeline_doc:
      return None
    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]
    
    for stage in pipeline_stages:
      if '$match' in stage:
        if quality is not None:
          stage['$match']['reward_choices']['$elemMatch']['choices']['$all'][0]['$elemMatch']['choices']['$elemMatch']['name'] = quality
          stage['$match']['reward_choices']['$elemMatch']['choices']['$all'][1]['$elemMatch']['choices']['$elemMatch']['name'] = item
        else:
          stage['$match']['reward_choices']['$elemMatch']['choices']['$elemMatch']['choices']['$elemMatch']['name'] = item
    levels = list(current_app.mongo_db.levels.aggregate(pipeline_stages))
    for level in levels:
      level['_id'] = str(level['_id'])
    return sorted(levels, key=lambda l:l.get('name'))