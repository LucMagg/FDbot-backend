from typing import Dict

from enum import Enum

class Quality(Enum):
    MAGIC = 1
    EPIC = 2
    MYTHIC = 3
    LEGENDARY = 4
    EXALTED = 5
    DIVINE = 6

class Reward:
  def __init__(self, quantity: int, appearances: int, type: str):
    self.quantity = quantity
    self.appearances = appearances
    self.type = type

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      quantity= data.get('quantity'),
      appearances= data.get('appearances'),
      type= data.get('type')
    )

  def to_dict(self) -> Dict:
    return {
      "quantity": self.quantity,
      "appearances": self.appearances,
      "type": self.type
    }

class GoldReward(Reward):
  def __init__(self, quantity: int, appearances: int):
    Reward.__init__(self, quantity, appearances, "gold")

class PotionsReward(Reward):
  def __init__(self, quantity: int, appearances: int):
    Reward.__init__(self, quantity, appearances, "potions")

class GearReward(Reward):
  def __init__(self, quality: Quality, appearances: int):
    Reward.__init__(self, 1, appearances, "gear")
    self.quality = quality

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      quality=data.get('quality'),
      appearances=data.get('appearances'),
    )

  def to_dict(self) -> Dict:
    return {
      "quantity": self.quantity,
      "appearances": self.appearances,
      "quality": self.quality,
      "type": self.type
    }

class DustReward(Reward):
  def __init__(self, quantity: int, quality: Quality, appearances: int):
    Reward.__init__(self, quantity, appearances, "dust")
    self.quality = quality

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      quantity=data.get('quantity'),
      quality=data.get('quality'),
      appearances=data.get('appearances')
    )

  def to_dict(self) -> Dict:
    return {
      "quantity": self.quantity,
      "appearances": self.appearances,
      "quality": self.quality,
      "type": self.type
    }