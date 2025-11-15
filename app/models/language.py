from bson import ObjectId
from typing import Dict, Optional, Union, List
from ..utils.strUtils import str_to_slug


class Language:
  def __init__(self, name: str, code: str, translations: List, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.code = code
    self.translations = translations

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('Name'),
      code = data.get('Code'),
      translations = data.get('Translations'),
    )

  def to_dict(self) -> Dict:
    language = {
      'name': self.name,
      'code': self.code,
      'translations': self.translations,
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