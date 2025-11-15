from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.langchannel import LangChannel


class LangChannelService:

  @staticmethod
  def create_langchannel(langchannel_data):
    langchannel = LangChannel.from_dict(langchannel_data)
    return langchannel.create(current_app.mongo_db)

  @staticmethod
  def get_one_langchannel(langchannel_channel_id_or_object_id):
    try:
      langchannel_obj = LangChannel.read_by_id(current_app.mongo_db, ObjectId(langchannel_channel_id_or_object_id))
      return langchannel_obj if langchannel_obj else None
    except InvalidId:
      pass

    langchannel_obj = LangChannel.read_by_name(current_app.mongo_db, langchannel_channel_id_or_object_id)
    return langchannel_obj if langchannel_obj else None
  
  @staticmethod
  def get_all_langchannels():
    return LangChannel.read_all(current_app.mongo_db)
  
  @staticmethod
  def update_langchannel(langchannel_data):
    try:
      if langchannel_data.get('_id'):
        langchannel_obj = LangChannel.read_by_id(current_app.mongo_db, ObjectId(langchannel_data.get('id')))
        return LangChannel.update_by_id(current_app.mongo_db, ObjectId(langchannel_data.get('id')), langchannel_data) if langchannel_obj else None
    except InvalidId:
      pass
    if langchannel_data.get('channel_id'):
      langchannel_obj = LangChannel.read_by_channel_id(current_app.mongo_db, langchannel_data.get('channel_id'))
      return LangChannel.update_by_channel_id(current_app.mongo_db, langchannel_data.get('channel_id'), langchannel_data) if langchannel_obj else None
    return None
  
  @staticmethod
  def delete_langchannel(langchannel_data):
    try:
      if langchannel_data.get('_id'):
        langchannel_obj = LangChannel.read_by_id(current_app.mongo_db, ObjectId(langchannel_data.get('id')))
        return LangChannel.delete_by_id(current_app.mongo_db, ObjectId(langchannel_data.get('id'))) if langchannel_obj else None
    except InvalidId:
      pass
    if langchannel_data.get('channel_id'):
      langchannel_obj = LangChannel.read_by_channel_id(current_app.mongo_db, langchannel_data.get('channel_id'))
      return LangChannel.delete_by_channel_id(current_app.mongo_db, langchannel_data.get('channel_id')) if langchannel_obj else None
    return None