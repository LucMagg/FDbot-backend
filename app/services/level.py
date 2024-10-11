from flask import current_app
from app.models.level import Level


class LevelService:

  @staticmethod
  def add_level(level_data):
    level = Level.from_dict(level_data)
    return Level.add_level(current_app.mongo_db, level_data)

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
    print(level_name)
    if level:
      return Level.add_reward(current_app.mongo_db, level.to_dict(), reward_data)
    return None
  
  def set_new_reward_types():
    return Level.build_new_levels(current_app.mongo_db)