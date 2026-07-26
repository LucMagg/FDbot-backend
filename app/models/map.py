from bson import ObjectId
from bson.errors import InvalidId
from typing import Dict, Optional
from ..utils.strUtils import str_to_slug


class Pics:
  def __init__(self, name: str, image_url: Optional[str] = None):
    self.name = name
    self.image_url = image_url

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name'),
      image_url = data.get('image_url')
    )
  
  def to_dict(self) -> Dict:
    return {
      'name': self.name,
      'image_url': self.image_url
    }
  

class Map:
  def __init__(self, name: str, name_slug: str, has_water_or_lava: bool, pics: list[Pics], _id: Optional[str] = None):
    try:
      self._id = ObjectId(_id) if _id else None
    except InvalidId:
      self._id = None
    self.name = name
    self.name_slug = name_slug
    self.has_water_or_lava = has_water_or_lava
    self.pics = pics if pics else []
    

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')),
      name = data.get('name'),
      name_slug = str_to_slug(data.get('name')),
      has_water_or_lava = data.get('has_water_or_lava'),
      pics = [Pics.from_dict(pic) for pic in data.get('pics', [])] if data.get('pics') else []
    )

  def to_dict(self) -> Dict:
    d = {
      'name': self.name,
      'name_slug': self.name_slug,
      'has_water_or_lava': self.has_water_or_lava,
      'pics': [pic.to_dict() for pic in self.pics]
    }
    if self._id:
      d['_id'] = str(self._id)
    return d

  def create(self, db):
    if not self._id:
      result = db.maps.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      data = self.to_dict()
      data.pop('_id', None)
      db.maps.update_one({'_id': self._id}, {'$set': data})
    return self  

  @staticmethod
  def read_by_id(db, map_id):
    data = db.maps.find_one({'_id': ObjectId(map_id)})
    return Map.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, map_name):
    data = db.maps.find_one({'name_slug': str_to_slug(map_name)})
    return Map.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.maps.find()
    return [Map.from_dict(map) for map in data] if data else None
  
  @staticmethod
  def update_one(db, map):
    map_to_update = map.copy()
    map_id = map_to_update.pop('_id', None)
    map_data = db.maps.update_one({'_id': ObjectId(map_id)}, {'$set': map_to_update})
    if map_data.modified_count > 0 or map_data.matched_count > 0:
      return map
    return None
  
  @staticmethod
  def update(db, data):
    map = {
      'has_water_or_lava': True if len(data) > 1 else False,
      'pics': []
    }
    for m in data:
      if 'with' in m.get('name'):
        map['pics'].append({'name': m.get('name').split('with')[1].strip(), 'image_url': m.get('image_url')})
        map['name'] = m.get('name').split('with')[0].strip()
        if 'water' in m.get('name'):
          map['pics'].append({'name': 'neutral', 'image_url': m.get('image_url')})
      else:
        map['name'] = m.get('name')
        map['pics'].append({'name': 'neutral', 'image_url': m.get('image_url')})
    map['name_slug'] = str_to_slug(map.get('name'))
    existing = Map.read_by_name(db, map.get('name'))
    if existing:
      existing.has_water_or_lava = map.get('has_water_or_lava')
      existing.pics = [Pics.from_dict(p) for p in map.get('pics')]
      existing.create(db)
    else:
      new_map = Map(
        name=map.get('name'),
        name_slug=map.get('name_slug'),
        has_water_or_lava=map.get('has_water_or_lava'),
        pics=[Pics.from_dict(p) for p in map.get('pics')]
      )
      new_map.create(db)