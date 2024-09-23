from bson import ObjectId
from typing import Dict, Optional
from ..utils.strUtils import str_to_slug


class Price_in_gems:
  def __init__(self, price: int, quantity: int): 
    self.price = price
    self.quantity = quantity

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      price = data.get('price'),
      quantity = data.get('quantity')
    )

  def to_dict(self) -> Dict:
    return {
      "price": self.price,
      "quantity": self.quantity
    }
  

class InputOutput:
  def __init__(self, name: Optional[str] = None, quantity: Optional[int] = None): 
    self.name = name or None
    self.quantity = quantity or None

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
  

class Conversion:
  def __init__(self, input: InputOutput, output: InputOutput):
    self.input = input
    self.output = output
  
  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      input = InputOutput.from_dict(data.get('input', {})),
      output = InputOutput.from_dict(data.get('output', {}))
    )

  def to_dict(self) -> Dict:
    return {
      "input": self.input.to_dict(),
      "output": self.output.to_dict()
    }


class Dust:
  def __init__(self, name: str, name_slug: str, icon: str, price_in_gems: Price_in_gems, grade: int, conversion: Optional[Conversion] = None, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.name_slug = name_slug
    self.icon = icon
    self.price_in_gems = price_in_gems
    self.grade = grade
    self.conversion = conversion

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id', {})),
      name = data.get('name'),
      name_slug = str_to_slug(data.get('name')),
      icon = data.get('icon'),
      price_in_gems = Price_in_gems.from_dict(data.get('price_in_gems', {})),
      grade = data.get('grade'),
      conversion = Conversion.from_dict(data.get('conversion', {})) if data.get('conversion') else None
    )

  def to_dict(self) -> Dict:
    result = {
      "_id": str(self._id) if self._id else None,
      "name": self.name,
      "name_slug": self.name_slug,
      "icon": self.icon,
      "grade": self.grade,
      "price_in_gems": self.price_in_gems.to_dict(),
    }
    if self.conversion:
      result["conversion"] = self.conversion.to_dict()
    return result

  def create(self, db):
    if not self._id:
      result = db.dusts.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.dusts.update_one({"_id": self._id}, {"$set": self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, dust_id):
    data = db.dusts.find_one({"_id": ObjectId(dust_id)})
    return Dust.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, dust_name):
    data = db.dusts.find_one({"name_slug": str_to_slug(dust_name)})
    return Dust.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.dusts.find()
    return [Dust.from_dict(dust) for dust in data] if data else None
  
  @staticmethod
  def update_by_name(db, dust_name, update_data):
    result = db.dusts.update_one({"name_slug": str_to_slug(dust_name)}, {"$set": update_data})
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def update_by_id(db, dust_id, update_data):
    result = db.dusts.update_one({"_id": ObjectId(dust_id)}, {"$set": update_data})
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def delete_by_name(db, dust_name):
    result = db.dusts.delete_one({"name_slug": str_to_slug(dust_name)})
    return result.deleted_count if result.deleted_count > 0 else None
  
  @staticmethod
  def delete_by_id(db, dust_id):
    result = db.dusts.delete_one({"_id": ObjectId(dust_id)})
    return result.deleted_count if result.deleted_count > 0 else None