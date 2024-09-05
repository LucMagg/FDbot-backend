from bson import ObjectId
from typing import Dict, Optional, Union, List
from ..utils.strUtils import str_to_slug


class Choice:
  def __init__(self, name: str, value: str):
    self.name = name
    self.value = value

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name'),
      value = data.get('value')
    )
  
  def to_dict(self) -> Dict:
    return {
      'name': self.name,
      'type': self.value
    }


class Option:
  def __init__(self, name: str, type: int, description: str, required: bool, choices: Union[List[Choice], List] = None):
    self.name = name
    self.type = type
    self.description = description
    self.required = required
    self.choices = choices

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name'),
      type = data.get('type'),
      description = data.get('description'),
      required = data.get('required'),
      choices = [Choice.from_dict(choice_data) for choice_data in data.get('choices', []) if isinstance(choice_data, dict)]
    )
  
  def to_dict(self) -> Dict:
    return {
      'name': self.name,
      'type': self.type,
      'description': self.description,
      'required': self.required,
      'choices': [choice.to_dict() for choice in self.choices] if self.choices else []
    }
  

class Command:
  def __init__(self, name: str, type: int, description: str, _id: Optional[str] = None, options: Union[List[Option], List] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.type = type
    self.description = description
    self.options = options

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name'),
      type = data.get('type'),
      description = data.get('description'),
      options = [Option.from_dict(option_data) for option_data in data.get('options', []) if isinstance(option_data, dict)]
    )

  def to_dict(self) -> Dict:
    command = {
      'name': self.name,
      'type': self.type,
      'description': self.description,
      'options': [option.to_dict() for option in self.options] if self.options else []
    }
    if self._id:
      command['_id'] = str(self._id)
    return command

  def create(self, db):
    if not self._id:
      result = db.commands.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.commands.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, command_id):
    data = db.commands.find_one({'_id': ObjectId(command_id)})
    return Command.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, command_name):
    data = db.commands.find_one({'name': command_name})
    return Command.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.commands.find()
    return [Command.from_dict(command) for command in data] if data else None
  
  @staticmethod
  def update_by_name(db, command_name, update_data):
    result = db.commands.update_one({'name': command_name}, {'$set': update_data})
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def update_by_id(db, command_id, update_data):
    result = db.commands.update_one({'_id': ObjectId(command_id)}, {'$set': update_data})
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def delete_by_name(db, command_name):
    result = db.commands.delete_one({'name': command_name})
    return result.deleted_count if result.deleted_count > 0 else None
  
  @staticmethod
  def delete_by_id(db, command_id):
    result = db.commands.delete_one({'_id': ObjectId(command_id)})
    return result.deleted_count if result.deleted_count > 0 else None