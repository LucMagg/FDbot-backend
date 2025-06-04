from bson import ObjectId
from typing import Dict, Optional, List
from ..utils.strUtils import str_to_slug


class PicInfo:
  def __init__(self, name: str, url: str):
    self.name = name
    self.url = url

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name'),
      url = data.get('url')
    )
  
  def to_dict(self) -> Dict:
    return {
      "name": self.name,
      "url": self.url
    }
  

class ChannelRepo:
  def __init__(self, channel: str, url: str):
    self.channel = channel
    self.url = url   
  
  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      channel = data.get('channel'),
      url = data.get('url')
    )
  
  def to_dict(self) -> Dict:
    return {
      "channel": self.channel,
      "url": self.url
    }
  

class Map:
  def __init__(self, name: str, name_slug: str, has_water_or_lava: bool, type: str, gameplay: str, map: List[List[str]], start: List[List[str]], pic_repository: List[ChannelRepo] = None, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.name_slug = name_slug
    self.has_water_or_lava = has_water_or_lava
    self.type = type
    self.gameplay = gameplay
    self.map = map
    self.start = start
    self.pic_repository = pic_repository if pic_repository else []

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id', {})),
      name = data.get('name'),
      name_slug = str_to_slug(data.get('name')),
      has_water_or_lava = data.get('has_water_or_lava'),
      type = str_to_slug(data.get('type')),
      gameplay = str_to_slug(data.get('gameplay')),
      map = data.get('map', []),
      start = data.get('start', []),
      pic_repository = [ChannelRepo.from_dict(repo) for repo in data.get('pic_repository', [])] if data.get('pic_repository') else []
    )

  def to_dict(self) -> Dict:
    return {
      "_id": str(self._id) if self._id else None,
      "name": self.name,
      "name_slug": self.name_slug,
      "has_water_or_lava": self.has_water_or_lava,
      "type": self.type,
      "gameplay": self.gameplay,
      "map": self.map,
      "start": self.start,
      "pic_repository": [repo.to_dict() for repo in self.pic_repository]
    }

  def create(self, db):
    if not self._id:
      result = db.maps.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.maps.update_one({"_id": self._id}, {"$set": self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, map_id):
    data = db.maps.find_one({"_id": ObjectId(map_id)})
    return Map.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, map_name):
    data = db.maps.find_one({"name_slug": str_to_slug(map_name)})
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