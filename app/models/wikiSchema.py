from bson import ObjectId
from typing import Dict, Optional, Union, List
from app.utils.types import *


class Property:
  def __init__(self, base: str, then: List[str]):
    self.base = base
    self.then = then
  
  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      base = data.get('base', ''),
      then = data.get('then', [])
    )

  def to_dict(self) -> Dict:
    return {
      'base': self.base,
      'then': self.then
    }


class Data:
  def __init__(self, row: Union[int, List[int], str], type: str, property: Union[str, Property], schema: str):
    self.row = row
    self.type = type
    self.property = property
    self.schema = schema

  @classmethod
  def from_dict(cls, data: Dict):
    row = data.get('row')
    property_data = data.get('property')
    
    if isinstance(property_data, dict):
      property = Property.from_dict(property_data)
    else:
      property = property_data

    return cls(
      row = row,
      type = data.get('type', ''),
      property = property,
      schema = data.get('schema', '')
    )

  def to_dict(self) -> Dict:
    property_dict = self.property.to_dict() if isinstance(self.property, Property) else self.property
    return {
      'row': self.row,
      'type': self.type,
      'property': property_dict,
      'schema': self.schema
    }
  

class WikiSchema:
  def __init__(self, name: str, type: str, data: Optional[List[Data]] = None, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.data = data or []
    self.type = type

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name', ''),
      data = [Data.from_dict(d) for d in data.get('data', []) if isinstance(d, dict)],
      type = data.get('type', '')
    )

  def to_dict(self) -> Dict:
    return {
      '_id': str(self._id) if self._id else None,
      'name': self.name,
      'data': [d.to_dict() for d in self.data],
      'type': self.type
    }
  
  def create(self, db):
    if not self._id:
      result = db.wikiSchemas.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.wikiSchemas.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self

  @staticmethod
  def read_by_id(db, wikiSchema_id):
    data = db.wikiSchemas.find_one({'_id': ObjectId(wikiSchema_id)})
    return WikiSchema.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, wikiSchema_name):
    data = db.wikiSchemas.find_one({'name': wikiSchema_name})
    return WikiSchema.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    return [WikiSchema.from_dict(wikiSchema) for wikiSchema in db.wikiSchemas.find()]