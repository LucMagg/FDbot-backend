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
      'value': self.value
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
  

class Language:
  def __init__(self, name: str, type: int, description: str, to_update: bool, setup_type: Optional[str] = None, _id: Optional[str] = None, options: Union[List[Option], List] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.type = type
    self.setup_type = setup_type
    self.to_update = to_update
    self.description = description
    self.options = options

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name'),
      type = data.get('type'),
      setup_type = data.get('setup_type'),
      to_update = data.get('to_update'),
      description = data.get('description'),
      options = [Option.from_dict(option_data) for option_data in data.get('options', []) if isinstance(option_data, dict)]
    )

  def to_dict(self) -> Dict:
    language = {
      'name': self.name,
      'type': self.type,
      'setup_type': self.setup_type,
      'to_update': self.to_update,
      'description': self.description,
      'options': [option.to_dict() for option in self.options] if self.options else []
    }
    if self._id:
      language['_id'] = str(self._id)
    return language

  def create(self, db):
    if not self._id:
      result = db.languages.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.languages.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, language_id):
    data = db.languages.find_one({'_id': ObjectId(language_id)})
    return Language.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, language_name):
    data = db.languages.find_one({'name': language_name})
    return Language.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.languages.find()
    return [Language.from_dict(language) for language in data] if data else None
  
  @staticmethod
  def update_by_name(db, language_name, update_data):
    result = db.languages.update_one({'name': language_name}, {'$set': update_data})
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def update_by_id(db, language_id, update_data):
    result = db.languages.update_one({'_id': ObjectId(language_id)}, {'$set': update_data})
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def delete_by_name(db, language_name):
    result = db.languages.delete_one({'name': language_name})
    return result.deleted_count if result.deleted_count > 0 else None
  
  @staticmethod
  def delete_by_id(db, language_id):
    result = db.languages.delete_one({'_id': ObjectId(language_id)})
    return result.deleted_count if result.deleted_count > 0 else None