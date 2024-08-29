from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.message import Message


class MessageService:

  @staticmethod
  def create_message(message_data):
    message = Message.from_dict(message_data)
    return message.create(current_app.mongo_db)

  @staticmethod
  def get_one_message(message_name_or_id):
    try:
      message_obj = Message.read_by_id(current_app.mongo_db, ObjectId(message_name_or_id))
      return message_obj if message_obj else None
    except InvalidId:
      pass

    message_obj = Message.read_by_name(current_app.mongo_db, message_name_or_id)
    return message_obj if message_obj else None
  
  @staticmethod
  def get_all_messages():
    return Message.read_all(current_app.mongo_db)