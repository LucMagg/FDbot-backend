from flask import current_app
from app.models.level import Level


class LevelService:

  @staticmethod
  def create_level(level_data):
    level = Level.from_dict(level_data)
    return level.create(current_app.mongo_db)

  @staticmethod
  def get_one_level(level_name):
    level_obj = Level.read_by_level(current_app.mongo_db, level_name)
    return level_obj if level_obj else None

  @staticmethod
  def get_all_levels():
    return Level.read_all(current_app.mongo_db)

  @staticmethod
  def add_reward(level_name, reward_data):
    level = Level.read_by_level(current_app.mongo_db, level_name)
    if level:
      return level.add_reward(current_app.mongo_db, reward_data)
    return None

  @staticmethod
  def get_expected_reward(level_name):
    level = Level.read_by_level(current_app.mongo_db, level_name)
    if level:
      return level.expected_reward()
    return None
  
  def set_new_reward_types():
    return Level.build_new_levels(current_app.mongo_db)