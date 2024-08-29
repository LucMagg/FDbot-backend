from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.dust import Dust


class DustService:

  @staticmethod
  def create_dust(dust_data):
    dust = Dust.from_dict(dust_data)
    return dust.create(current_app.mongo_db)

  @staticmethod
  def get_one_dust(dust_name_or_id):
    try:
      dust_obj = Dust.read_by_id(current_app.mongo_db, ObjectId(dust_name_or_id))
      return dust_obj if dust_obj else None
    except InvalidId:
      pass

    dust_obj = Dust.read_by_name(current_app.mongo_db, dust_name_or_id)
    return dust_obj if dust_obj else None
  
  @staticmethod
  def get_all_dusts():
    return Dust.read_all(current_app.mongo_db)