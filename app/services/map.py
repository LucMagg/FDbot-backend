from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.map import Map


class MapService:

  @staticmethod
  def create_map(map_data):
    map = Map.from_dict(map_data)
    return map.create(current_app.mongo_db)
  
  @staticmethod
  def get_all_maps():
    return Map.read_all(current_app.mongo_db)
  
  @staticmethod
  def update_map(map_data):
    return Map.update_one(current_app.mongo_db, map_data)