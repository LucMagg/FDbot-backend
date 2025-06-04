from flask import current_app
from app.models.spireConfig import SpireConfig


class SpireConfigService:
  @staticmethod
  def add_channel(new_channel_id, type):
    return SpireConfig.add_one_channel(current_app.mongo_db, new_channel_id, type)
 
  @staticmethod
  def get_all_channels():
    return SpireConfig.read_all_channels(current_app.mongo_db)
  
  @staticmethod
  def get_all_map_bonuses():
    return SpireConfig.read_all_map_bonuses(current_app.mongo_db)