from flask import current_app
from bson.objectid import ObjectId
from app.models.level import Level

class LevelService:

  @staticmethod
  def create_level(level_data):
    level = Level.from_dict(level_data)
    return level.create(current_app.mongo_db)

  @staticmethod
  def get_one_level_by_id(level_id):
    level_obj = Level.read_by_id(current_app.mongo_db, ObjectId(level_id))
    return level_obj if level_obj else None

  @staticmethod
  def get_one_level(level_name, level_floor, level_number):
    level_obj = Level.read_by_level(current_app.mongo_db, level_name, level_floor, level_number)
    return level_obj if level_obj else None

  @staticmethod
  def get_all_levels():
    return Level.read_all(current_app.mongo_db)