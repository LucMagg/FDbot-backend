from bson import ObjectId
from typing import Dict, Optional


class XpMinMax:
  def __init__(self, min: int, max: int):
    self.min = min
    self.max = max

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      min = data.get('min'),
      max = data.get('max')
    )
  
  def to_dict(self) -> Dict:
    return {
      "min": self.min,
      "max": self.max
    }
  
class LevelThreshold:
  def __init__(self, level: XpMinMax, threshold: int|None):
    self.level = level
    self.threshold = threshold

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      level = XpMinMax.from_dict(data.get('level')),
      threshold = data.get('threshold')
    )
  
  def to_dict(self) -> Dict:
    return {
      "level": self.level.to_dict(),
      "threshold": self.threshold
    }

class XpThreshold:
  def __init__(self, hero_stars: int, A0: LevelThreshold, A1: LevelThreshold, A2: LevelThreshold, A3: LevelThreshold):
    self.hero_stars = hero_stars
    self.A0 = A0
    self.A1 = A1
    self.A2 = A2
    self.A3 = A3

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      hero_stars = data.get('hero_stars'),
      A0 = LevelThreshold.from_dict(data.get('A0')),
      A1 = LevelThreshold.from_dict(data.get('A1')),
      A2 = LevelThreshold.from_dict(data.get('A2')),
      A3 = LevelThreshold.from_dict(data.get('A3'))
    )
  
  def to_dict(self) -> Dict:
    result = {
      "hero_stars": self.hero_stars,
      "A0": self.A0.to_dict(),
      "A1": self.A1.to_dict(),
      "A2": self.A2.to_dict(),
      "A3": self.A3.to_dict()
    }
    return result
  

class XpData:
  def __init__(self, level: int, A0: int|None, A1: int|None, A2: int|None, A3: int|None):
    self.level = level
    self.A0 = A0
    self.A1 = A1
    self.A2 = A2
    self.A3 = A3

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      level = data.get('level'),
      A0 = data.get('A0'),
      A1 = data.get('A1'),
      A2 = data.get('A2'),
      A3 = data.get('A3')
    )

  def to_dict(self) -> Dict:
    result = {
      "level": self.level,
      "A0": self.A0,
      "A1": self.A1,
      "A2": self.A2,
      "A3": self.A3
    }
    return result

class HeroXp:
  def __init__(self, hero_stars: int, data: list[XpData], _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.hero_stars = hero_stars
    self.data = data

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id', {})),
      hero_stars = data.get('hero_stars'),
      data = [XpData.from_dict(xp) for xp in data.get('data', []) if isinstance(xp, dict)],
    )

  def to_dict(self) -> Dict:
    result = {
      "_id": str(self._id) if self._id else None,
      "hero_stars": self.hero_stars,
      "data": [xp.to_dict() for xp in self.data] if self.data else []
    }
    return result

  @staticmethod
  def read_all(db):
    data = db.heroXp.find()
    return [HeroXp.from_dict(xp) for xp in data] if data else None
  

  @staticmethod
  def read_thresholds(db):
    data = db.xpThresholds.find()
    return [XpThreshold.from_dict(xp) for xp in data] if data else None