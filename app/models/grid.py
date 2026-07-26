from bson import ObjectId
from bson.errors import InvalidId
from typing import Dict, Optional, List
from ..utils.strUtils import str_to_slug


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
      'channel': self.channel,
      'url': self.url
    }
  

class Grid:
  def __init__(self, name: str, name_slug: str, image_url: str, pic_repository: List[ChannelRepo] = None, _id: Optional[str] = None):
    try:
      self._id = ObjectId(_id) if _id else None
    except InvalidId:
      self._id = None
    self.name = name
    self.name_slug = name_slug
    self.image_url = image_url
    self.pic_repository = pic_repository if pic_repository else []

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')),
      name = data.get('name'),
      name_slug = str_to_slug(data.get('name')),
      image_url = data.get('image_url'),
      pic_repository = [ChannelRepo.from_dict(repo) for repo in data.get('pic_repository', [])] if data.get('pic_repository') else []
    )

  def to_dict(self) -> Dict:
    data = {
      'name': self.name,
      'name_slug': self.name_slug,
      'image_url': self.image_url,
      'pic_repository': [repo.to_dict() for repo in self.pic_repository]
    }
    if self._id:
      data['_id'] = self._id
    return data

  def create(self, db):
    if not self._id:
      result = db.grids.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.grids.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, grid_id):
    data = db.grids.find_one({'_id': ObjectId(grid_id)})
    return Grid.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, grid_name):
    data = db.grids.find_one({'name_slug': str_to_slug(grid_name)})
    return Grid.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.grids.find()
    return [Grid.from_dict(grid) for grid in data] if data else None
    
  @staticmethod
  def update(db, data):
    for grid in data:
      existing = Grid.read_by_name(db, grid.get('name'))
      if existing:
        existing.image_url = grid.get('image_url')
        existing.create(db)
      else:
        new_grid = Grid(
          name=grid.get('name'),
          name_slug=str_to_slug(grid.get('name')),
          image_url=grid.get('image_url')
        )
        new_grid.create(db)