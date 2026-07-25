from bson import ObjectId
from typing import Dict, Optional, Union, List
from ..utils.strUtils import str_to_slug


class Choice:
  def __init__(self, name: str, name_localizations: Dict[str,str], value: str):
    self.name = name
    self.name_localizations = name_localizations
    self.value = value

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name'),
      name_localizations = data.get('name_localizations'),
      value = data.get('value')
    )
  
  def to_dict(self) -> Dict:
    return {
      'name': self.name,
      'name_localizations': self.name_localizations,
      'value': self.value
    }


class Option:
  def __init__(self, name: str, name_localizations: dict, type: int, description: str, description_localizations: dict, required: bool, choices: Union[List[Choice], List] = None, options: Union[List['Option'], List] = None):
    self.name = name
    self.name_localizations = name_localizations
    self.type = type
    self.description = description
    self.description_localizations = description_localizations
    self.required = required
    self.choices = choices
    self.options = options

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name'),
      name_localizations = data.get('name_localizations'),
      type = data.get('type'),
      description = data.get('description'),
      description_localizations = data.get('description_localizations'),
      required = data.get('required'),
      choices = [Choice.from_dict(choice_data) for choice_data in data.get('choices', []) if isinstance(choice_data, dict)],
      options = [Option.from_dict(o) for o in data.get('options', []) if isinstance(o, dict)]
    )
  
  def to_dict(self) -> Dict:
    return {
      'name': self.name,
      'name_localizations': self.name_localizations,
      'type': self.type,
      'description': self.description,
      'description_localizations': self.description_localizations,
      'required': self.required,
      'choices': [c.to_dict() for c in self.choices] if self.choices else [],
      'options': [o.to_dict() for o in self.options] if self.options else []
    }
  

class Command:
  def __init__(self, name: str, name_localizations: dict, type: int, description: str, description_localizations: dict, to_update: bool, setup_type: Optional[str] = None, _id: Optional[str] = None, options: Union[List[Option], List] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.name_localizations = name_localizations
    self.type = type
    self.setup_type = setup_type
    self.to_update = to_update
    self.description = description
    self.description_localizations = description_localizations
    self.options = options

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name'),
      name_localizations = data.get('name_localizations'),
      type = data.get('type'),
      setup_type = data.get('setup_type'),
      to_update = data.get('to_update'),
      description = data.get('description'),
      description_localizations = data.get('description_localizations'),
      options = [Option.from_dict(option_data) for option_data in data.get('options', []) if isinstance(option_data, dict)]
    )

  def to_dict(self) -> Dict:
    command = {
      'name': self.name,
      'name_localizations': self.name_localizations,
      'type': self.type,
      'setup_type': self.setup_type,
      'to_update': self.to_update,
      'description': self.description,
      'description_localizations': self.description_localizations,
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