from flask import current_app
from app.models.dc import Dc


class DcService:
  @staticmethod
  def post_dc(dc_data):
    dc = Dc.from_dict(dc_data)
    return dc.create(current_app.mongo_db)

  @staticmethod
  def get_one_level(dc_level: str):
    dc_obj = Dc.read(current_app.mongo_db, dc_level)
    return dc_obj if dc_obj else None

  @staticmethod
  def get_all_levels():
    return Dc.read_all(current_app.mongo_db)
  
  @staticmethod
  def clear_dc():
    return Dc.clear(current_app.mongo_db)