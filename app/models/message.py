from bson import json_util, ObjectId
from ..utils.strUtils import str_to_slug


class Message:
  @staticmethod
  def to_json(data):
    return json_util.dumps(data)

  @staticmethod
  def from_json(json_data):
    return json_util.loads(json_data)

  @staticmethod
  def create(db, new_message):
    new_message['name_slug'] = str_to_slug(new_message['name'])
    result = db.messages.insert_one(new_message)
    return str(result.inserted_id)

  @staticmethod
  def read_by_name(db, message_name):
    message = db.messages.find_one({"name_slug": str_to_slug(message_name)})
    if message:
      message['_id'] = str(message['_id'])
      return message
    return None
  
  @staticmethod
  def read_by_id(db, message_id):
    message = db.messages.find_one({"_id": ObjectId(message_id)})
    if message:
      message['_id'] = str(message['_id'])
      return message
    return None

  @staticmethod
  def read_all(db):
    messages = list(db.messages.find())
    if messages:
      for message in messages:  
        message['_id'] = str(message['_id'])
      return messages
    return None

  @staticmethod
  def update_by_name(db, message_name, update_data):
    result = db.messages.update_one({"name_slug": str_to_slug(message_name)}, {"$set": update_data})
    return result.modified_count > 0

  @staticmethod
  def update_by_id(db, message_id, update_data):
    result = db.messages.update_one({"_id": ObjectId(message_id)}, {"$set": update_data})
    return result.modified_count > 0

  @staticmethod
  def delete_by_name(db, message_name):
    result = db.messages.delete_one({"name_slug": str_to_slug(message_name)})
    return result.deleted_count > 0
  
  @staticmethod
  def delete_by_id(db, message_id):
    result = db.messages.delete_one({"_id": ObjectId(message_id)})
    return result.deleted_count > 0