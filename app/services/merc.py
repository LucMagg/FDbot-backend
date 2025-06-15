from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.merc import Merc


class MercService:

  @staticmethod
  def create_or_update_user(merc_data):
    merc = Merc.from_dict(merc_data)
    return merc.create(current_app.mongo_db)

  @staticmethod
  def get_user(user_or_id):
    try:
      merc_obj = Merc.read_by_id(current_app.mongo_db, ObjectId(user_or_id))
      current_app.logger.req("read by _id")
      return merc_obj if merc_obj else None
    except:
      pass
    
    merc_obj = Merc.read_by_user_id(current_app.mongo_db, user_or_id)
    if merc_obj:
      current_app.logger.req("read by user_id")
      return merc_obj

    current_app.logger.req("read by user")
    merc_obj = Merc.read_by_user(current_app.mongo_db, user_or_id)
    return merc_obj if merc_obj else None
  
  @staticmethod
  def get_users_by_merc(merc):
    return Merc.read_by_merc(current_app.mongo_db, merc)
  
  @staticmethod
  def get_all_mercs():
    return Merc.read_all_unique_mercs(current_app.mongo_db)
  
  @staticmethod
  def get_all_users():
    result = Merc.read_all(current_app.mongo_db)
    return [{"user": r.get('user'), "user_id": r.get('user_id')} for r in result] if result else None