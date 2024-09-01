from bson import ObjectId
from typing import Dict, Optional
from ..utils.strUtils import str_to_slug


class Level:
  def __init__(self, name: str, floor: int, number: int, cost: int, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.floor = floor
    self.number = number
    self.cost = cost

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = str_to_slug(data.get('name')),
      floor = data.get('floor'),
      number = data.get('number'),
      cost= data.get('cost')
    )

  def to_dict(self) -> Dict:
    level = {
      "name": self.name,
      "floor": self.floor,
      "number": self.number,
      "cost": self.cost
    }
    if self._id:
      level["_id"] = str(self._id)

    return level

  def create(self, db):
    if not self._id:
      result = self.read_by_level(db, self.name, self.floor, self.number)
      if result:
        return result
      result = db.levels.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.levels.update_one({"_id": self._id}, {"$set": self.to_dict()})
    return self

  @staticmethod
  def read_by_id(db, level_id):
    data = db.levels.find_one({"_id": ObjectId(level_id)})
    return Level.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, level_name):
    data = db.levels.find_one({"name_slug": str_to_slug(level_name)})
    return Level.from_dict(data) if data else None

  @staticmethod
  def read_by_level(db, level_name, level_floor, level_number):
    data = db.levels.find_one({"name": str_to_slug(level_name), "floor": level_floor, "number": level_number})
    return Level.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    return [Level.from_dict(level) for level in db.levels.find()]