from bson import ObjectId
from typing import Dict, Optional
from ..utils.strUtils import str_to_slug


class DustRecycling:
  def __init__(self, name: str, quantity: int):
    self.name = name
    self.quantity = quantity

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name'),
      quantity = data.get('quantity')
    )

  def to_dict(self) -> Dict:
    return {
      "name": self.name,
      "quantity": self.quantity
    }


class Recycling:
  def __init__(self, gold: int, dust: DustRecycling):
    self.gold = gold
    self.dust = dust

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      gold = data.get('gold'),
      dust = DustRecycling.from_dict(data.get('dust'))
    )

  def to_dict(self) -> Dict:
    return {
      "gold": self.gold,
      "dust": self.dust.to_dict()
    }


class Quality:
  def __init__(self, name: str, name_slug: str, icon: str, price: int, recycling: Recycling, type: str, grade: int, discount_price: Optional[int] = None, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.name_slug = name_slug
    self.icon = icon
    self.price = price
    self.discount_price = discount_price
    self.recycling = recycling
    self.type = type
    self.grade = grade

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id', {})),
      name = data.get('name'),
      name_slug = str_to_slug(data.get('name')),
      icon = data.get('icon'),
      price = data.get('price'),
      discount_price = data.get('discount_price'),
      recycling = Recycling.from_dict(data.get('recycling')),
      type = data.get('type'),
      grade = data.get('grade')
    )

  def to_dict(self) -> Dict:
    return {
      "_id": str(self._id) if self._id else None,
      "name": self.name,
      "name_slug": self.name_slug,
      "icon": self.icon,
      "price": self.price,
      "discount_price": self.discount_price,
      "recycling": self.recycling.to_dict(),
      "type": self.type,
      "grade": self.grade
    }
  
  def create(self, db):
    if not self._id:
      result = db.qualities.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.qualities.update_one({"_id": self._id}, {"$set": self.to_dict()})
    return self

  @staticmethod
  def read_by_id(db, quality_id):
    data = db.qualities.find_one({"_id": ObjectId(quality_id)})
    return Quality.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, quality_name):
    data = db.qualities.find_one({"name_slug": str_to_slug(quality_name)})
    return Quality.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    return [Quality.from_dict(quality) for quality in db.qualities.find()]

  @staticmethod
  def read_by_type(db, type):
    qualities = [Quality.from_dict(quality) for quality in db.qualities.find()]
    return [quality for quality in qualities if quality.type == type]
  
  @staticmethod
  def update_by_name(db, quality_name, update_data):
    result = db.qualities.update_one({"name_slug": str_to_slug(quality_name)}, {"$set": update_data})
    return result.modified_count > 0

  @staticmethod
  def update_by_id(db, quality_id, update_data):
    result = db.qualities.update_one({"_id": ObjectId(quality_id)}, {"$set": update_data})
    return result.modified_count > 0

  @staticmethod
  def delete_by_name(db, quality_name):
    result = db.qualities.delete_one({"name_slug": str_to_slug(quality_name)})
    return result.deleted_count > 0
  
  @staticmethod
  def delete_by_id(db, quality_id):
    result = db.qualities.delete_one({"_id": ObjectId(quality_id)})
    return result.deleted_count > 0