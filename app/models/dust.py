from bson import ObjectId
from typing import Dict, Optional
from ..utils.strUtils import str_to_slug


class LocalizedText:
  def __init__(self, values: Dict[str, str], default_lang: str = 'en'):
    self.values = values or {}
    self.default_lang = default_lang

  def get(self, lang: Optional[str] = None) -> Optional[str]:
    if not self.values:
      return None
    lang = lang or self.default_lang
    return self.values.get(lang) or self.values.get(self.default_lang) or next(iter(self.values.values()))

  def set(self, lang: str, value: str):
    self.values[lang] = value

  def to_dict(self) -> Dict[str, str]:
    return self.values

  @classmethod
  def from_dict(cls, data, default_lang: str = 'en'):
    if isinstance(data, dict):
      return cls(data, default_lang)
    if isinstance(data, str):
      return cls({default_lang: data}, default_lang)
    return cls({}, default_lang)

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
      'price': self.price,
      'quantity': self.quantity
    }
  

class InputOutput:
  def __init__(self, name: Optional[LocalizedText] = None, quantity: Optional[int] = None): 
    self.name = name or None
    self.quantity = quantity or None

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = LocalizedText.from_dict(data.get('name')) or None,
      quantity = data.get('quantity')
    )

  def to_dict(self) -> Dict:
    return {
      'name': self.name.to_dict() or None,
      'quantity': self.quantity
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
      'input': self.input.to_dict(),
      'output': self.output.to_dict()
    }


class Dust:
  def __init__(self, name: LocalizedText, name_slug: str, icon: str, price_in_gems: Price_in_gems, grade: int, conversion: Optional[Conversion] = None, _id: Optional[str] = None):
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
      name = LocalizedText.from_dict(data.get('name')),
      name_slug = data.get('name_slug'),
      icon = data.get('icon'),
      price_in_gems = Price_in_gems.from_dict(data.get('price_in_gems', {})),
      grade = data.get('grade'),
      conversion = Conversion.from_dict(data.get('conversion', {})) if data.get('conversion') else None
    )

  def to_dict(self) -> Dict:
    result = {
      '_id': str(self._id) if self._id else None,
      'name': self.name.to_dict(),
      'name_slug': self.name_slug,
      'icon': self.icon,
      'grade': self.grade,
      'price_in_gems': self.price_in_gems.to_dict(),
    }
    if self.conversion:
      result['conversion'] = self.conversion.to_dict()
    return result

  def create(self, db):
    if not self._id:
      result = db.dusts.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.dusts.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, dust_id):
    data = db.dusts.find_one({'_id': ObjectId(dust_id)})
    return Dust.from_dict(data) if data else None
  
  @staticmethod
  def read_by_slug(db, dust_slug):
    data = db.dusts.find_one({'name_slug': dust_slug})
    return Dust.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.dusts.find()
    return [Dust.from_dict(dust) for dust in data] if data else None