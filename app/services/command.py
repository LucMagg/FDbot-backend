from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.command import Command


class CommandService:

  @staticmethod
  def create_command(command_data):
    command = Command.from_dict(command_data)
    return command.create(current_app.mongo_db)

  @staticmethod
  def get_one_command(command_name_or_id):
    try:
      command_obj = Command.read_by_id(current_app.mongo_db, ObjectId(command_name_or_id))
      return command_obj if command_obj else None
    except InvalidId:
      pass

    command_obj = Command.read_by_name(current_app.mongo_db, command_name_or_id)
    return command_obj if command_obj else None
  
  @staticmethod
  def get_all_commands():
    return Command.read_all(current_app.mongo_db)