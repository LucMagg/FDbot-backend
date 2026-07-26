from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.traprole import TrapRole


class TrapRoleService:

  @staticmethod
  def create_traprole(traprole_data):
    traprole = TrapRole.from_dict(traprole_data)
    return traprole.create(current_app.mongo_db)

  @staticmethod
  def get_one_traprole(traprole_guild_id_or_object_id):
    try:
      traprole_obj = TrapRole.read_by_id(current_app.mongo_db, ObjectId(traprole_guild_id_or_object_id))
      return traprole_obj if traprole_obj else None
    except InvalidId:
      pass

    traprole_obj = TrapRole.read_by_name(current_app.mongo_db, traprole_guild_id_or_object_id)
    return traprole_obj if traprole_obj else None
  
  @staticmethod
  def get_all_traproles():
    return TrapRole.read_all(current_app.mongo_db)
  
  @staticmethod
  def update_traprole(traprole_data):
    try:
      if traprole_data.get('_id'):
        traprole_obj = TrapRole.read_by_id(current_app.mongo_db, ObjectId(traprole_data.get('id')))
        return TrapRole.update_by_id(current_app.mongo_db, ObjectId(traprole_data.get('id')), traprole_data) if traprole_obj else None
    except InvalidId:
      pass
    if traprole_data.get('guild_id'):
      traprole_obj = TrapRole.read_by_guild_id(current_app.mongo_db, traprole_data.get('guild_id'))
      return TrapRole.update_by_guild_id(current_app.mongo_db, traprole_data.get('guild_id'), traprole_data) if traprole_obj else None
    return None
  
  @staticmethod
  def delete_traprole(traprole_data):
    try:
      if traprole_data.get('_id'):
        traprole_obj = TrapRole.read_by_id(current_app.mongo_db, ObjectId(traprole_data.get('id')))
        return TrapRole.delete_by_id(current_app.mongo_db, ObjectId(traprole_data.get('id'))) if traprole_obj else None
    except InvalidId:
      pass
    if traprole_data.get('guild_id'):
      traprole_obj = TrapRole.read_by_guild_id(current_app.mongo_db, traprole_data.get('guild_id'))
      return TrapRole.delete_by_guild_id(current_app.mongo_db, traprole_data.get('guild_id')) if traprole_obj else None
    return None