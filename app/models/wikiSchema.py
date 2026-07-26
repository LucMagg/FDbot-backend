from bson import ObjectId
from typing import Dict, Optional, List
from app.utils.types import *



class Fields:
  def __init__(
      self,
      name: str,
      selector: str,
      extract: Optional[str] = None,
      prefix: Optional[str] = None,
      start: Optional[int] = None,
      step: Optional[int] = None,
      count: Optional[int] = None,
      transform: Optional[str] = None,
      transform_all: Optional[str] = None,
      multiple: Optional[bool] = False,
      attribute: Optional[str] = None,
  ):
    self.name = name
    self.selector = selector
    self.extract = extract
    self.prefix = prefix
    self.start = start
    self.step = step
    self.count = count
    self.transform = transform
    self.transform_all = transform_all
    self.multiple = multiple
    self.attribute = attribute

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name', ''),
      selector = data.get('selector', ''),
      extract = data.get('extract', None),
      prefix = data.get('prefix', None),
      start = data.get('start', None),
      step = data.get('step', None),
      count = data.get('count', None),
      transform = data.get('transform', None),
      transform_all = data.get('transform_all', None),
      multiple = data.get('multiple', False),
      attribute = data.get('attribute', None)
    )

  def to_dict(self) -> Dict:
    return {
      'name': self.name,
      'selector': self.selector,
      'extract': self.extract or None,
      'prefix': self.prefix or None,
      'start': self.start or None,
      'step': self.step or None,
      'count': self.count or None,
      'prefix': self.prefix or None,
      'transform': self.transform or None,
      'transform_all': self.transform_all or None,
      'multiple': self.multiple or False,
      'attribute': self.attribute or None
    }


class Follow:
  def __init__(
      self,
      field: str,
      base_selector: str,
      into: str,
      fields: Optional[List[Fields]] = None,
  ):
    self.field = field
    self.base_selector = base_selector
    self.into = into
    self.fields = fields or []

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      field = data.get('field', ''),
      base_selector = data.get('base_selector', ''),
      into = data.get('into', ''),
      fields = [Fields.from_dict(f) for f in data.get('fields', []) if isinstance(f, dict)],
    )

  def to_dict(self) -> Dict:
    return {
      'field': self.field,
      'base_selector': self.base_selector,
      'into': self.into,
      'fields': [f.to_dict() for f in self.fields],
    }

class WikiSchema:
  def __init__(
      self,
      name: str,
      type: str,
      base_selector: str,
      group: Optional[str] = None,
      fields: Optional[List[Fields]] = None,
      follow: Optional[Follow] = None,
      no_header_skip: Optional[bool] = False,
      parse_type: Optional[str] = None,
      _id: Optional[str] = None,
    ):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.fields = fields or []
    self.type = type
    self.base_selector = base_selector
    self.group = group
    self.follow = follow
    self.no_header_skip = no_header_skip
    self.parse_type = parse_type

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name', ''),
      fields = [Fields.from_dict(f) for f in data.get('fields', []) if isinstance(f, dict)],
      type = data.get('type', ''),
      base_selector = data.get('base_selector', ''),
      group = data.get('group', ''),
      follow = Follow.from_dict(data['follow']) if data.get('follow') else None,
      no_header_skip = data.get('no_header_skip', False),
      parse_type = data.get('parse_type', None),
    )

  def to_dict(self) -> Dict:
    return {
      '_id': str(self._id) if self._id else None,
      'name': self.name,
      'fields': [f.to_dict() for f in self.fields],
      'type': self.type,
      'base_selector': self.base_selector,
      'group': self.group,
      'follow': self.follow.to_dict() if self.follow else None,
      'no_header_skip': self.no_header_skip or False,
      'parse_type': self.parse_type or None
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